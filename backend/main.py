from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from database import initialize_db
from routes import auth as auth_routes
from routes import profile as profile_routes
from mongo import init_mongo, close_mongo
from redis_client import init_redis, close_redis

load_dotenv()

app = FastAPI(title="Login App API", version="1.0.0")

# Allow the React frontend hosted on Vite to talk to this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://login-form-pf76-git-main-pavin-kalyaans-projects.vercel.app/login"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create the database tables and ensure profile fields exist (SQLite fallback).
initialize_db()


@app.on_event("startup")
async def on_startup():
    try:
        await init_mongo(app)
        print("MongoDB connected")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")

    try:
        await init_redis(app)
        print("Redis connected")
    except Exception as e:
        print(f"Redis connection failed: {e}")


@app.on_event("shutdown")
async def on_shutdown():
    # Close external services
    await close_redis(app)
    await close_mongo(app)

# Attach route groups from the auth and profile files.
app.include_router(auth_routes.router)
app.include_router(profile_routes.router)


@app.get("/")
def home():
    return {"message": "Login API is running"}
