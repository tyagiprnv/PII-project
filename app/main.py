from fastapi import FastAPI, Response, BackgroundTasks
from app.schemas import RedactRequest, RedactResponse
from app.verification import verifier
from app.service import redactor
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import json

# NEW METRIC: Track how many times the Auditor finds a leak
AUDITOR_LEAK_DETECTIONS = Counter("auditor_leaks_found_total", "Number of PII leaks caught by the LLM Auditor")

REDACTION_COUNT = Counter("total_redactions", "Number of redactions performed")
CONFIDENCE_HISTOGRAM = Histogram("model_confidence_scores", "Distribution of model confidence", buckets=[0, 0.5, 0.7, 0.8, 0.9, 1.0])

app = FastAPI(title="Iron-Clad AI Gateway", version="1.0.0")

async def audit_redaction_task(redacted_text: str, token_mapping_keys: list):
    """
    This runs in the background. It asks the LLM to find leaks.
    If a leak is found, it nukes the Redis record.
    """
    try:
        result_raw = await verifier.check_for_leaks(redacted_text)
        
        # Robust JSON parsing (LLMs sometimes wrap JSON in markdown blocks)
        if isinstance(result_raw, str):
            # Clean markdown if present
            clean_json = result_raw.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_json)
        else:
            result = result_raw

        if result.get("leaked"):
            AUDITOR_LEAK_DETECTIONS.inc() # Update our health dashboard
            print(f"🚨 SECURITY ALERT: LLM found a leak: {result.get('reason')}")
            
            for key in token_mapping_keys:
                redactor.db.delete(key)
            print(f"🔒 PURGE COMPLETE: Removed {len(token_mapping_keys)} keys from Redis.")
            
    except Exception as e:
        print(f"Error in background audit: {e}")

@app.post("/redact")
async def redact_data(request: RedactRequest, background_tasks: BackgroundTasks):
    # 1. Redact and get the keys created for THIS request
    clean_text, scores, keys = redactor.redact_and_store(request.text)
    
    # 2. Add the audit task to the background queue
    # We pass the 'keys' so the auditor knows exactly what to delete if it finds a leak
    background_tasks.add_task(audit_redaction_task, clean_text, keys)
    
    # 3. Metrics
    REDACTION_COUNT.inc()
    for score in scores:
        CONFIDENCE_HISTOGRAM.observe(score)
        
    return {
        "redacted_text": clean_text, 
        "confidence_scores": scores, 
        "audit_status": "queued"
    }

@app.post("/restore")
async def restore_data(redacted_text: str):
    # This pulls data back from Redis
    original = redactor.restore(redacted_text)
    return {"original_text": original}

@app.get("/metrics")
def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)