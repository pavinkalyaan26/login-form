from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
)
from mongo import get_users_collection
from redis_client import get_redis
from schemas import Token, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    request: Request,
    users=Depends(get_users_collection),
):
    existing_user = await users.find_one({"email": user.email})

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    hashed_password = get_password_hash(user.password)

    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "age": None,
        "gender": None,
        "address": None,
        "interests": None,
        "bio": None,
        "created_at": datetime.utcnow(),
    }

    result = await users.insert_one(new_user)

    user_id = str(result.inserted_id)

    token = create_access_token(
        {
            "sub": user_id
        }
    )

    redis = get_redis(request)

    if redis is not None:
        await redis.set(
            f"session:{user_id}",
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
    users=Depends(get_users_collection),
):
    saved_user = await users.find_one(
        {
            "email": user.email
        }
    )

    if (
        saved_user is None
        or not verify_password(
            user.password,
            saved_user["password"],
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    user_id = str(saved_user["_id"])

    token = create_access_token(
        {
            "sub": user_id
        }
    )

    redis = get_redis(request)

    if redis is not None:
        await redis.set(
            f"session:{user_id}",
            token,
            ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    return {
        "access_token": token,
        "token_type": "bearer",
    }