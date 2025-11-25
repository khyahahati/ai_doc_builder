# backend/app/schemas/revision.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class RevisionBase(BaseModel):
    section_id: int
    version: int
    content: str
    score: Optional[float] = None


class RevisionCreate(RevisionBase):
    pass


class RevisionResponse(RevisionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
