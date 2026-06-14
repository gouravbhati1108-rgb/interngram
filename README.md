# Interngram v1.0

Trust-based internship platform for engineering students.

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Docker & Docker Compose

### 1. Start infrastructure

```bash
docker compose up -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
copy ..\.env.example ..\.env
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Seed Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@interngram.com | AdminPass123! |
| Student | student1@test.com | StudentPass123! |
| Company | company1@test.com | CompanyPass123! |

## Architecture

- **Backend:** FastAPI + PostgreSQL + Redis + S3 (LocalStack)
- **Frontend:** Next.js 15 + Tailwind CSS
- **Auth:** JWT (httpOnly cookies) + CSRF + Admin MFA
- **Docs:** See `docs/api.md` and `docs/ranking-formula.md`

## Testing

```bash
cd backend && pytest
cd frontend && npm test
```
