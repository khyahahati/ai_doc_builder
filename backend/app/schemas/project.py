from datetime import datetime

from pydantic import BaseModel, ConfigDict


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

    model_config = ConfigDict(from_attributes=True)
