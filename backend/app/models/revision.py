from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db import Base


class Revision(Base):
    __tablename__ = "revisions"

    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("sections.id"), nullable=False)

    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)

    score = Column(Float, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    section = relationship("Section", back_populates="revisions")
