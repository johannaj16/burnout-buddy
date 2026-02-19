# Postgres Setup (Backend)

## 1) Start Postgres (Docker)

```powershell
cd c:\Users\johan\burnout-buddy\backend
docker compose up -d postgres
```

## 2) Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Configure DATABASE_URL

```powershell
$env:DATABASE_URL = "postgresql+psycopg://burnout:burnout@localhost:5432/burnout_buddy"
```

Optional persistent local env file:
- Copy `backend/.env.example` to `.env` and load it via your shell tooling.

## 4) Initialize schema

The app auto-creates tables at startup (`init_db_schema()` in `app/main.py`).

Optional manual SQL route:

```powershell
docker exec -i burnout-buddy-postgres psql -U burnout -d burnout_buddy < sql/001_create_evenings.sql
```

## 5) Run API

```powershell
uvicorn app.main:app --reload
```

## 6) Verify persistence

- Start API and call:
  - `POST /v1/evening/{id}/commands`
  - `GET /v1/evening/{id}/snapshot`
- Stop/restart API, call snapshot again, and confirm state remains.

## Notes

- If `DATABASE_URL` is missing, the backend falls back to in-memory store.
- For production, replace startup `create_all` with Alembic migrations.
