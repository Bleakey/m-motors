import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _token_from_request(request: Request) -> Optional[str]:
    """Extract token from cookie or Authorization header."""
    token = request.cookies.get("access_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ", 1)[1]
    return token


def get_user_from_token(token: str, db: Session) -> Optional[models.User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            return None
    except JWTError:
        return None
    return db.query(models.User).filter(models.User.email == email).first()


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[models.User]:
    token = _token_from_request(request)
    if not token:
        return None
    return get_user_from_token(token, db)


async def require_auth(
    request: Request,
    db: Session = Depends(get_db)
) -> models.User:
    user = await get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Non authentifié")
    return user


async def require_admin(
    request: Request,
    db: Session = Depends(get_db)
) -> models.User:
    user = await require_auth(request, db)
    if user.role != models.UserRole.admin:
        raise HTTPException(status_code=403, detail="Accès refusé")
    return user
