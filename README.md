# TaskDesk API

Task & inventory management REST API with a built-in web dashboard.

**Stack:** Python 3.12 · FastAPI · SQLAlchemy 2 · PostgreSQL · JWT (PyJWT + bcrypt) · Docker · pytest

## Features
- JWT authentication (register, login, `/me`) with bcrypt-hashed passwords
- Role-based access: `admin` manages inventory and sees all tasks; `user` manages only their own tasks and can read inventory
- CRUD for tasks and inventory, with pagination (`page`, `size`), search and filters
- Pydantic input validation (types, lengths, ranges, SKU format) with clear error messages
- Auto-generated OpenAPI docs at `/docs` and `/redoc`
- Dashboard UI at `/` (sign in, tasks, inventory, low-stock highlighting)
- 15 pytest tests, ~94% coverage, run on in-memory SQLite

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://localhost:8000 (UI) or http://localhost:8000/docs (Swagger).
Defaults to SQLite. A demo admin (`admin` / `admin12345`) and sample inventory are created on first start; change them with env vars (see `.env.example`).

## Run with Docker (PostgreSQL)
```bash
docker compose up --build
```

## Tests
```bash
pytest          # prints a coverage report
```

## Deploy to Render
1. Push this folder to a GitHub repo.
2. Render dashboard → **New → Blueprint** → pick the repo. `render.yaml` creates the web service and a free PostgreSQL database.
3. Enter a strong `ADMIN_PASSWORD` when asked. `SECRET_KEY` is generated for you.
4. Open the service URL. Health check: `/health`.

> Free Render services sleep when idle, so the first request after a break takes ~30 s. Free Postgres databases expire after a limited period; check Render's current terms.

## API overview
| Method | Path | Access |
|---|---|---|
| POST | `/api/auth/register` · `/api/auth/login` | public |
| GET | `/api/auth/me` | any user |
| GET/POST | `/api/tasks` | any user (own tasks; admin sees all) |
| GET/PUT/DELETE | `/api/tasks/{id}` | owner or admin |
| GET | `/api/items`, `/api/items/summary`, `/api/items/{id}` | any user |
| POST/PUT/DELETE | `/api/items`, `/api/items/{id}` | admin |
