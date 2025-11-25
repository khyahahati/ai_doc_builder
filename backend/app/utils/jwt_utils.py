import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status

# ---------------------------------------------
# JWT CONFIG
# ---------------------------------------------
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_THIS"   # ← change before production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24   # 24 hours


# ---------------------------------------------
# Create JWT Access Token
# ---------------------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates a signed JWT token with user data.
    """
    to_encode = data.copy()

    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# ---------------------------------------------
# Verify JWT Token & Extract Payload
# ---------------------------------------------
def verify_access_token(token: str):
    """
    Decodes the JWT token, validates signature + expiration.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # contains user_id, email, etc.

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please login again."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token."
        )
