# backend/app/schemas/project.py
from datetime import datetime
from pydantic import BaseModel


class ProjectBase(BaseModel):
    title: str
    doc_type: str  # "docx" or "pptx"


# Used for POST /projects
class ProjectCreate(ProjectBase):
    pass


# Used for responses: project detail, list, "my projects" etc.
class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        orm_mode = True
