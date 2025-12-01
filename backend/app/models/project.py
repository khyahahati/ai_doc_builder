from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)   # "docx" or "pptx"

    # Link to the user who owns this project
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="projects")
    sections = relationship(
        "Section",
        back_populates="project",
        cascade="all, delete-orphan"
    )
