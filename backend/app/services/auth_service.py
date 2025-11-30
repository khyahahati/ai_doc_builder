from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..models.user import User

# ----------------------------------------------------
# Password hashing (bcrypt)
# ----------------------------------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_password(password: str) -> str:
    """
    Ensures the password respects bcrypt's 72-byte limit.
    Truncates at the byte level and returns a safe UTF-8 string.
    """
    pw_bytes = password.encode("utf-8")

    # Already within limit
    if len(pw_bytes) <= 72:
        return password

    # Truncate safely and decode best-effort
    return pw_bytes[:72].decode("utf-8", errors="ignore")


def hash_password(password: str) -> str:
    """
    Hash password after enforcing bcrypt's 72-byte limit.
    """
    safe_pw = _normalize_password(password)
    return pwd_context.hash(safe_pw)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password using the same normalization rules.
    """
    safe_pw = _normalize_password(plain_password)
    return pwd_context.verify(safe_pw, hashed_password)


# ----------------------------------------------------
# Auth Logic
# ----------------------------------------------------
def create_user(db: Session, email: str, password: str):
    """
    Create a new user with hashed password.
    """
    # Check if user already exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    # Hash password safely
    hashed_pass = hash_password(password)

    new_user = User(
        email=email,
        hashed_password=hashed_pass
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Load DB-generated fields (id, created_at)

    return new_user
