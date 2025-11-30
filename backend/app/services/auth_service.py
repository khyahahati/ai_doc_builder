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
    if not isinstance(password, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be a string")

    safe_pw = _normalize_password(password)
    try:
        return pwd_context.hash(safe_pw)
    except ValueError as exc:
        # Re-raise as HTTPException with a clearer message for the API client
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password using the same normalization rules.
    """
    if not isinstance(plain_password, str):
        return False

    safe_pw = _normalize_password(plain_password)
    try:
        return pwd_context.verify(safe_pw, hashed_password)
    except ValueError:
        # Any backend/value error treated as verification failure
        return False


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

    # Defensive: ensure password is a string and within bcrypt's 72-byte limit.
    if not isinstance(password, str):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be a string.")
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too long. Maximum length is 72 bytes when encoded as UTF-8."
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
