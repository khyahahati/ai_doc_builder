from backend.app.db import SessionLocal
from backend.app.models.user import User
from backend.app.models.project import Project


def test_db():
    db = SessionLocal()

    print("\n=== DB Sanity Test ===")

    # 1. Query empty tables
    print("Users:", db.query(User).all())
    print("Projects:", db.query(Project).all())

    # 2. Insert dummy user
    new_user = User(email="test@example.com", hashed_password="abc123")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print("Inserted User:", new_user.id, new_user.email)

    # 3. Insert dummy project for this user
    new_project = Project(
        title="Sample Project",
        doc_type="docx",
        owner_id=new_user.id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    print("Inserted Project:", new_project.id, new_project.title)

    db.close()


if __name__ == "__main__":
    test_db()
