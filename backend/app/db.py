from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./ai_doc_builder.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


# Creates all tables based on the SQLAlchemy models.
def init_db() -> None:
    Base.metadata.create_all(bind=engine)


# ✅ Dependency used inside API routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
