import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from fastapi import Request

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://pavinkalyaan7_db_user:sspk7msd@task1.qndr4qm.mongodb.net/?appName=task1")
MONGODB_NAME = os.getenv("MONGODB_NAME", "task1")

async def init_mongo(app):
    """Initialize Motor client and attach to FastAPI app.state."""
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.get_database(MONGODB_NAME)
    app.state.mongo_client = client
    app.state.mongodb = db
    # Ensure indexes
    try:
        await db.users.create_index("email", unique=True)
    except Exception:
        pass

async def close_mongo(app):
    client: Optional[AsyncIOMotorClient] = getattr(app.state, "mongo_client", None)
    if client is not None:
        client.close()

def get_users_collection(request: Request):
    """FastAPI dependency to retrieve the users collection."""
    return request.app.state.mongodb["users"]
