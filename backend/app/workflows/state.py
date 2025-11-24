from typing import Optional, List
from pydantic import BaseModel

class SectionState(BaseModel):
    section_id: int
    section_title: str
    doc_type: str

    # ✅ NEW — user’s raw outline for refinement phase
    raw_outline: Optional[List[str]] = None

    # ✅ NEW — refined outline output
    refined_outline: Optional[List[str]] = None

    content: Optional[str] = None
    version: int = 1
    score: Optional[float] = None
    user_feedback: str = "pending"
    attempts: int = 0
    max_attempts: int = 3
    user_prompt: Optional[str] = None
    context_summary: Optional[str] = None
