# ---------- Builder Stage ----------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --user --no-cache-dir \
    fastapi==0.115.0 \
    "uvicorn[standard]==0.30.6" \
    sqlalchemy==2.0.36 \
    "pydantic>=2.11" \
    python-dotenv==1.0.1 \
    "passlib[bcrypt]==1.7.4" \
    "python-jose[cryptography]==3.3.0" \
    bcrypt==4.0.1 \
    motor==3.7.1 \
    pymongo==4.13.2 \
    redis[hiredis]==5.2.1 \
    email-validator==2.2.0

# ---------- Runtime Stage ----------
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

# Copy installed packages
COPY --from=builder /root/.local /root/.local

# Copy backend source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]