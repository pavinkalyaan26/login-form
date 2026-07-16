from fastapi import APIRouter, Depends, HTTPException, status, Request
from datetime import datetime
from bson import ObjectId

from auth import create_access_token, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from mongo import get_users_collection
from redis_client import get_redis
from schemas import Token, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, request: Request, users=Depends(get_users_collection), redis=Depends(get_redis)):
    """Create a new account and return a JWT token."""
    existing_user = await users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    doc = {
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
    res = await users.insert_one(doc)
    user_id = str(res.inserted_id)
    token = create_access_token({"sub": user_id})

    # store session token in Redis (optional)
    if redis is not None:
        try:
            await redis.set(f"session:{user_id}", token, ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        except Exception:
            pass

    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(user: UserLogin, request: Request, users=Depends(get_users_collection), redis=Depends(get_redis)):
    """Check user credentials and return a JWT token."""
    saved_user = await users.find_one({"email": user.email})
    if not saved_user or not verify_password(user.password, saved_user.get("password")):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(saved_user.get("_id"))
    token = create_access_token({"sub": user_id})

    if redis is not None:
        try:
            await redis.set(f"session:{user_id}", token, ex=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        except Exception:
            pass

    return {"access_token": token, "token_type": "bearer"}
