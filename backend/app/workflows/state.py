from typing import Optional
from pydantic import BaseModel

class SectionState(BaseModel):
    section_id: int
    content: Optional[str] = None
    version: int = 1
    score: Optional[float] = None
    user_feedback: str = "pending"  # pending | like | dislike
    attempts: int = 0
    max_attempts: int = 3
    user_prompt: Optional[str] = None
