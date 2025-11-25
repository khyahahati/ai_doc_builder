from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext

from backend.app.models.user import User

# ----------------------------------------------------
# Password hashing (bcrypt)
# ----------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ----------------------------------------------------
# Auth Logic
# ----------------------------------------------------
def create_user(db: Session, email: str, password: str):
    # check if user exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    hashed_pass = hash_password(password)

    new_user = User(
        email=email,
        hashed_password=hashed_pass
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)        # ← missing line added

    return new_user             # ← return user
