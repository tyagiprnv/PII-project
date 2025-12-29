import redis
import uuid
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

class RedactorService:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.db = redis.Redis(host='redis', port=6379, decode_responses=True)

    def redact_and_store(self, text: str):
        results = self.analyzer.analyze(text=text, language='en')
        
        # This list will track ONLY the keys created in THIS specific function call
        created_keys = []
        
        def store_in_redis(pii_text):
            token_id = uuid.uuid4().hex[:4]
            token = f"[REDACTED_{token_id}]"
            
            # Save mapping and track the key
            self.db.set(token, pii_text, ex=86400)
            created_keys.append(token) 
            return token

        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators={"DEFAULT": OperatorConfig("custom", {"lambda": store_in_redis})}
        )
        
        scores = [res.score for res in results]
        
        # Return the keys alongside the text and scores
        return anonymized_result.text, scores, created_keys

    def restore(self, redacted_text: str):
        import re
        tokens = re.findall(r"\[REDACTED_[a-z0-9]+\]", redacted_text)
        restored_text = redacted_text
        for token in tokens:
            original_value = self.db.get(token)
            if original_value:
                restored_text = restored_text.replace(token, original_value)
        return restored_text

redactor = RedactorService()