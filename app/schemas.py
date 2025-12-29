from pydantic import BaseModel, Field

class RedactRequest(BaseModel):
    text: str = Field(..., example="My name is Jane Doe and my email is jane@example.com")

class RedactResponse(BaseModel):
    original_length: int
    redacted_text: str
    entities_found: list[str]