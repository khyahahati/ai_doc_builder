import sys
import os

# ✅ ensure project root is in import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ai_doc_builder.backend.app.db import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)   # "docx" or "pptx"
    created_at = Column(DateTime, server_default=func.now())
