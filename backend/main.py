from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from database import initialize_db
from routes import auth as auth_routes
from routes import profile as profile_routes
from mongo import init_mongo, close_mongo
from redis_client import init_redis, close_redis

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Login App API",
    version="1.0.0"
)
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",

    # Vercel
    "https://login-formfrontend.vercel.app",

    # Render frontend (if you use it)
    "https://frontend-loginforms.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize local database (if your project uses it)
initialize_db()


@app.on_event("startup")
async def startup_event():
    print("Starting Login API...")

    # MongoDB
    try:
        await init_mongo(app)
        print("✅ MongoDB connected")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

    # Redis
    try:
        await init_redis(app)
        print("✅ Redis connected")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down Login API...")

    try:
        await close_redis(app)
        print("Redis disconnected")
    except Exception:
        pass

    try:
        await close_mongo(app)
        print("MongoDB disconnected")
    except Exception:
        pass


# Register API routes
app.include_router(auth_routes.router)
app.include_router(profile_routes.router)


@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Login API is running successfully"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }