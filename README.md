# Personal Finance Manager

[![CI](https://github.com/GabeMed/personal-financial-manager/actions/workflows/ci.yml/badge.svg)](https://github.com/GabeMed/personal-financial-manager/actions/workflows/ci.yml)

A personal finance app: users sign up, record income and expenses in their own
categories, and get a dashboard with the current balance and a breakdown of
spending and income per category.

- **Backend:** FastAPI, SQLAlchemy 2, Pydantic v2, JWT (OAuth2 password flow), PostgreSQL or SQLite. Layered as routers → services → CRUD → models.
- **Frontend:** React 19, TypeScript, Vite, Chakra UI v3, TanStack Query, React Hook Form + Zod, Recharts.

![Dashboard with balance, expense breakdown and transaction list](docs/screenshots/dashboard.png)

<details>
<summary>Editing a transaction</summary>

![Edit transaction dialog](docs/screenshots/edit-dialog.png)

</details>

## Quick start

Requires Docker.

```bash
git clone https://github.com/GabeMed/personal-financial-manager.git
cd personal-financial-manager
docker compose up --build
```

| URL | What |
| --- | --- |
| http://localhost:5173 | The app. Sign in as **demo / demo1234** (seeded on first start), or create an account. |
| http://localhost:8000/docs | Interactive API docs (Swagger). Use *Authorize* with the same credentials. |

`docker compose down -v` stops everything and wipes the database.

## Architecture

```mermaid
flowchart LR
    Browser["Browser<br/>React SPA"]

    subgraph frontend["frontend container"]
        Nginx["nginx<br/>static build + /api proxy"]
    end

    subgraph backend["backend container: FastAPI"]
        direction TB
        Routers["api/v1 routers<br/>auth · users · categories · transactions"]
        Auth["core<br/>JWT, bcrypt, settings"]
        Services["services<br/>business rules"]
        Crud["crud<br/>SQLAlchemy queries"]
        Routers --> Auth
        Routers --> Services --> Crud
    end

    DB[("PostgreSQL 16<br/>(SQLite for local dev/tests)")]

    Browser -- "HTML/JS" --> Nginx
    Browser -- "/api/v1/* + Bearer token" --> Nginx
    Nginx -- "proxy" --> Routers
    Crud --> DB
```

**Request flow.** The SPA stores the JWT returned by `POST /api/v1/auth/token`
and an Axios interceptor attaches it to every request. `get_current_user`
resolves the token to a user, and every query is scoped by `user_id`, so users
can only see or modify their own categories and transactions (a request for
someone else's resource returns 404).

**Layers** (`backend/app/`):

| Layer | Responsibility |
| --- | --- |
| `api/v1/` | HTTP only: parse input with Pydantic schemas, call a service, return a response model. |
| `services/` | Business rules: category names unique per user, a transaction's category must belong to its owner, summary math. Raises `NotFoundError` / `ConflictError`, which `main.py` maps to 404 / 409. |
| `crud/` | SQLAlchemy queries and writes. |
| `models/`, `schemas/` | ORM entities (`User`, `Category`, `Transaction`) and request/response DTOs. |
| `core/` | Settings from environment variables, password hashing, JWT. |

**Balance.** Each user has a stored `balance`. Creating, updating or deleting a
transaction adjusts it in the same database transaction: the old effect of the
transaction (+amount for income, −amount for expense) is reverted and the new
one applied, so changing an amount, a type (income ↔ expense) or both keeps the
balance correct. The tests check this for every write path.

**Money** is stored as `NUMERIC(10, 2)` and handled as `Decimal` on the server;
API responses emit JSON numbers for the frontend.

## Running without Docker

Backend (Python 3.12). Run from the repository root, because the code imports
itself as `backend.app`. With no configuration it uses a local SQLite file
(`./app.db`).

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
python -m backend.app.seed                      # optional: demo / demo1234
uvicorn backend.app.main:app --reload --port 8000
```

Frontend (Node 22):

```bash
cd frontend/finance-app
npm ci
npm run dev        # http://localhost:5173, talks to http://localhost:8000/api/v1
```

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest                                   # in-memory SQLite, a fresh DB per test
TEST_DATABASE_URL=postgresql+psycopg://user:pass@localhost:5432/db pytest   # PostgreSQL
ruff check . && ruff format --check .
```

38 API-level tests cover:

- **Auth:** registration and validation, duplicate username/e-mail, login, wrong password, missing/invalid/expired tokens.
- **Categories:** create/list, per-user isolation, case-insensitive duplicates (409), empty or too-long names.
- **Transactions:** create/list/paginate (newest first), amount and type validation, PATCH of amount / type / category / description with the balance checked after each change, delete, using another user's category or transaction (404).
- **Summary:** totals, per-category percentages, inclusive date range.
- **Seed:** idempotent, and the balance matches the seeded transactions.

Frontend checks: `npm run lint` and `npm run build` (which runs `tsc -b`).

[CI](.github/workflows/ci.yml) runs on every push and pull request: ruff and
pytest on SQLite and PostgreSQL, frontend lint and build, then a smoke test
that runs `docker compose up --wait` and signs in as the demo user through the
nginx proxy.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///./app.db` | SQLAlchemy URL; compose uses `postgresql+psycopg://finance:finance@db:5432/finance`. |
| `SECRET_KEY` | `dev-only-insecure-key` | JWT signing key. **Set this outside local development.** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token lifetime. |
| `CORS_ORIGINS` | `http://localhost:5173` | Comma-separated allowed origins. |
| `SEED_DEMO_DATA` | `false` (`true` in compose) | Create the demo user on startup. |
| `VITE_API_URL` | `http://localhost:8000/api/v1` | Frontend build-time API base URL (`/api/v1` in the Docker image). |

See [.env.example](.env.example).

## API

| Method | Route | Description |
| --- | --- | --- |
| POST | `/api/v1/users/register` | Create an account |
| POST | `/api/v1/auth/token` | Log in (form fields `username`, `password`), returns a JWT |
| GET | `/api/v1/users/me` | Current user, including balance |
| GET | `/api/v1/categories/all` | List own categories |
| POST | `/api/v1/categories` | Create a category |
| GET | `/api/v1/transactions/all?skip=&limit=` | List own transactions, newest first (limit ≤ 100) |
| POST | `/api/v1/transactions` | Create a transaction |
| PATCH | `/api/v1/transactions/{id}` | Partially update a transaction |
| DELETE | `/api/v1/transactions/{id}` | Delete a transaction |
| GET | `/api/v1/transactions/summary?start=&end=` | Balance, income/expense totals and % per category |
| GET | `/health` | Liveness check |

## Known limitations

- No migrations: tables are created with `create_all()` on startup. Alembic would be the next step before any schema change.
- The transaction list has pagination but no filters (date range, category) yet, and the frontend only loads the first page.
- The JWT lives in `localStorage`; there are no refresh tokens.
- Timestamps are stored without a time zone (UTC by convention).
- No frontend unit tests yet; the frontend is checked by lint, type-check and build.

## Documentation in Portuguese

The original technical write-up (architecture, directory layout, design
decisions and priorities) is in [docs/README.pt-BR.md](docs/README.pt-BR.md).
