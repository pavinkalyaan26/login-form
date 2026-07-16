from fastapi import APIRouter, Depends, Header, HTTPException, status, Request
from bson import ObjectId

from auth import decode_access_token
from mongo import get_users_collection
from redis_client import get_redis
from schemas import UserRead, UserUpdate

router = APIRouter(prefix="/profile", tags=["profile"])


async def get_current_user(authorization: str | None = Header(default=None), users=Depends(get_users_collection), redis=Depends(get_redis)):
    """Read the bearer token and return the matching MongoDB user document."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # verify server-side session in Redis if available
    if redis is not None:
        try:
            stored = await redis.get(f"session:{user_id}")
            if stored is None or stored != token:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session invalid or expired")
        except HTTPException:
            raise
        except Exception:
            pass

    user = await users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # normalize for Pydantic: convert _id to str id
    user["id"] = str(user.get("_id"))
    return user


@router.get("", response_model=UserRead)
async def get_profile(current_user=Depends(get_current_user)):
    """Return the current logged-in user's profile."""
    return current_user


@router.put("", response_model=UserRead)
async def update_profile(profile_data: UserUpdate, current_user=Depends(get_current_user), users=Depends(get_users_collection)):
    """Update the authenticated user's profile fields in MongoDB."""
    update_data = {k: v for k, v in profile_data.model_dump(exclude_none=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    await users.update_one({"_id": ObjectId(current_user["id"])}, {"$set": update_data})
    user = await users.find_one({"_id": ObjectId(current_user["id"])})
    user["id"] = str(user.get("_id"))
    return user
