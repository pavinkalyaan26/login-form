# Login App

This workspace contains a full-stack login application with:
- React + Vite frontend
- FastAPI backend
- SQLite database
- JWT authentication
- Protected dashboard

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

## Notes

- The frontend expects the backend at http://127.0.0.1:8000
- Login and registration use JWT tokens stored in localStorage
- The dashboard shows the current profile and includes a logout button
