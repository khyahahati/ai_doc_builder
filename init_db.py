from backend.app.db import Base, engine
from backend.app.models import project, section, revision

Base.metadata.create_all(bind=engine)

print("✅ Database tables created!")
