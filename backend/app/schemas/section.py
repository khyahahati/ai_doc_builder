from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


# ---------- Base section shape ----------
class SectionBase(BaseModel):
    title: str


# Used internally when creating sections from outline
class SectionCreate(SectionBase):
    project_id: int


# Response shape for a section
class SectionResponse(SectionBase):
    id: int
    project_id: int
    content: Optional[str] = None
    version: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Outline input from user ----------
class OutlineInput(BaseModel):
    sections: List[str]
    """
    Example JSON:
    {
      "sections": ["Introduction", "Problem Statement", "Methodology", "Conclusion"]
    }
    """


# ---------- For refine endpoint later (like/dislike + custom instructions) ----------
class SectionRefineRequest(BaseModel):
    feedback: str  # "like" or "dislike"
    user_prompt: Optional[str] = None
