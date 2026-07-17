from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from auth import (
    create_access_token,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from database import get_db
from models import User
from schemas import Token, UserCreate, UserLogin
from redis_client import get_redis

router = APIRouter(prefix="/auth", tags=["auth"])


def find_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    existing_user = find_user_by_email(db, user.email)

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(
        {"sub": new_user.email}
    )

    redis = get_redis(request)

    if redis is not None:
        await redis.set(
            f"session:{new_user.email}",
            token,
            ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token)
async def login(
    user: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
):
    saved_user = find_user_by_email(
        db,
        user.email,
    )

    if (
        not saved_user
        or not verify_password(
            user.password,
            saved_user.password,
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    token = create_access_token(
        {"sub": saved_user.email}
    )

    redis = get_redis(request)

    if redis is not None:
        await redis.set(
            f"session:{saved_user.email}",
            token,
            ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        # Debug (remove later)
        print("Redis Session Created")
        print(await redis.get(f"session:{saved_user.email}"))

    return {
        "access_token": token,
        "token_type": "bearer",
    }