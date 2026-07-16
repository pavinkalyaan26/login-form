import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_NAME = os.getenv("MONGODB_NAME", "inittask")


async def init_mongo(app):
    """
    Initialize MongoDB connection and attach it to app.state.
    """

    if not MONGODB_URI:
        raise RuntimeError("MONGODB_URI is missing in .env")

    try:
        client = AsyncIOMotorClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000
        )

        # Verify the connection
        await client.admin.command("ping")

        db = client[MONGODB_NAME]

        app.state.mongo_client = client
        app.state.mongodb = db

        # Create unique email index
        await db.users.create_index("email", unique=True)

        print("✅ Connected to MongoDB Atlas")

    except Exception as e:
        print("❌ MongoDB connection failed")
        print(e)
        raise


async def close_mongo(app):
    """
    Close MongoDB connection.
    """
    client: Optional[AsyncIOMotorClient] = getattr(
        app.state,
        "mongo_client",
        None,
    )

    if client:
        client.close()
        print("MongoDB connection closed")


def get_users_collection(request: Request):
    """
    Dependency that returns the users collection.
    """
    return request.app.state.mongodb["users"]