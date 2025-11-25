from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from ai_doc_builder.backend.app.db import Base


class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)

    version = Column(Integer, default=1)
    status = Column(String, default="pending")  # pending | generated | refined

    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="sections")
    revisions = relationship(
        "Revision",
        back_populates="section",
        cascade="all, delete-orphan"
    )
