from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)
