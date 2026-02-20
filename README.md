# Production CRUD API Template

Opinionated FastAPI CRUD starter with API key auth, pagination, and in-memory rate limiting.

## Features
- CRUD routes for `items`
- API key guard (`X-API-Key`)
- Query pagination (`limit`, `offset`)
- Request rate limiting middleware
- Pytest coverage for happy path and auth checks

## Quick start
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir src
```

Use API key: `X-API-Key: dev-api-key`

## Test
```bash
pytest -q
```

## Next upgrades
- Swap in PostgreSQL + SQLAlchemy
- Add Alembic migrations
- Add JWT + role-based auth
- Add structured logging + metrics