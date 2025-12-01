from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=func.now())

    # one user → many projects
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
