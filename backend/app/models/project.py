import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.app.db import Base


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
