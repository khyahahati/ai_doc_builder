# init_db.py
from backend.app.db import Base, engine
from backend.app.models import user, project, section, revision

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")
