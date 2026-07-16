import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Use SQLite by default, or the URL from .env if present.
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def initialize_db():
    """Create database tables and add new profile columns if needed."""
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    with engine.begin() as connection:
        if "age" not in existing_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN age INTEGER"))
        if "gender" not in existing_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN gender VARCHAR(50)"))
        if "address" not in existing_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN address VARCHAR(255)"))
        if "interests" not in existing_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN interests VARCHAR(255)"))
        if "bio" not in existing_columns:
            connection.execute(text("ALTER TABLE users ADD COLUMN bio VARCHAR(500)"))


def get_db():
    """Provide a database session to route handlers and close it cleanly."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
