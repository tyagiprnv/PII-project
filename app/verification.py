import httpx

class VerificationAgent:
    def __init__(self):
        self.ollama_url = "http://ollama:11434/api/generate"

    async def check_for_leaks(self, redacted_text: str):
        prompt = f"""
        You are a Privacy Security Auditor. Your job is to find any UNREDACTED 
        Personally Identifiable Information (PII) in the text below.
        PII includes: Names, Emails, SSNs, Phone Numbers, or ID numbers.
        Text to check: "{redacted_text}"
        
        Return ONLY a JSON object with:
        "leaked": true/false,
        "reason": "explanation of what was missed"
        """
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.ollama_url, json={
                    "model": "phi3",
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                })
                return response.json().get("response")
            except Exception as e:
                return {"leaked": False, "error": str(e)}

verifier = VerificationAgent()