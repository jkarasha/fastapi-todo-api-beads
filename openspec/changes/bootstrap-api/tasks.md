# Tasks: Bootstrap Todo API

## Overview
Ordered implementation tasks for building the FastAPI Todo API from scratch. Tasks are designed to be small, verifiable, and deliver incremental progress.

**Beads Tracking**: This plan is tracked in Beads. Use `bd list` to see current status, `bd ready` to see available work, and `bd blocked` to see dependency chains.

---

## Phase 1: Project Foundation
**Epic**: `fastapi-todo-api-beads-c4s`
**Goal**: Working dev environment with basic app skeleton

| Task | ID | Priority | Blocked By | Description |
|------|----|----------|------------|-------------|
| Create pyproject.toml with dependencies | c4s.5 | P1 | - | fastapi, sqlalchemy, aiosqlite, python-jose, passlib, pydantic-settings, alembic |
| Add dev dependencies to pyproject.toml | c4s.1 | P1 | - | pytest, pytest-asyncio, httpx, ruff, mypy |
| Run uv sync to create lockfile | c4s.2 | P2 | c4s.5, c4s.1 | Create lockfile and virtual environment |
| Create ruff.toml configuration | c4s.3 | P2 | - | line-length=88, Python 3.13 target |
| Create .gitignore | c4s.4 | P2 | - | venv, pycache, env, db files |
| Create src directory structure | c4s.6 | P1 | - | src/__init__.py and domain directories with __init__.py files |
| Create .env.example | c4s.7 | P2 | - | Document required environment variables |
| Create README.md | c4s.8 | P2 | - | Project documentation with setup instructions |
| **Validate**: verify FastAPI import works | c4s.9 | P1 | c4s.2 | `uv run python -c "import fastapi"` succeeds |

---

## Phase 2: Core Infrastructure
**Epic**: `fastapi-todo-api-beads-x5l`
**Goal**: Database connection, config, and error handling working
**Blocked By**: Phase 1 epic

| Task | ID | Priority | Blocked By | Description |
|------|----|----------|------------|-------------|
| Create src/core/config.py | x5l.5 | P1 | - | Settings class with DATABASE_URL, SECRET_KEY, etc. |
| Create src/core/database.py | x5l.1 | P1 | x5l.5 | Async engine and session factory |
| Create src/core/dependencies.py | x5l.2 | P1 | x5l.1 | get_db async generator |
| Create src/core/schemas.py | x5l.3 | P1 | - | BaseSchema class for consistent serialization |
| Create src/core/exceptions.py | x5l.4 | P1 | - | AppException base and common errors |
| Create src/main.py with FastAPI app | x5l.8 | P1 | x5l.4 | FastAPI app, exception handlers, /health endpoint |
| Initialize Alembic | x5l.6 | P1 | - | Run `alembic init alembic` (creates alembic.ini) |
| Configure alembic.ini after initialization | x5l.9 | P1 | x5l.6 | Customize alembic.ini with database URL and migration settings |
| Configure alembic/env.py for async | x5l.7 | P1 | x5l.6 | Async SQLAlchemy configuration |
| **Validate**: app starts and /health returns 200 | x5l.10 | P1 | x5l.8 | uvicorn starts, /health endpoint works |

---

## Phase 3: Authentication Domain
**Epic**: `fastapi-todo-api-beads-925`
**Goal**: User registration, login, and JWT authentication working
**Blocked By**: Phase 2 epic

| Task | ID | Priority | Blocked By | Description |
|------|----|----------|------------|-------------|
| Create src/auth/models.py | 925.5 | P1 | - | User SQLAlchemy model |
| Create Alembic migration for user table | 925.1 | P1 | 925.5 | Generate and run migration |
| Create src/auth/schemas.py | 925.2 | P1 | - | UserCreate, UserResponse, TokenResponse, LoginRequest |
| Create src/auth/exceptions.py | 925.3 | P1 | - | EmailExistsError, InvalidCredentialsError, etc. |
| Create src/auth/service.py | 925.4 | P1 | 925.2, 925.3 | Password hashing, user creation, authentication |
| Add JWT utilities to auth/service.py | 925.9 | P1 | 925.4 | create_token, decode_token functions |
| Create src/auth/dependencies.py | 925.6 | P1 | - | get_current_user dependency |
| Create src/auth/router.py | 925.7 | P1 | 925.4, 925.6 | /register, /login, /me endpoints per auth/spec.md |
| Mount auth router in main.py | 925.8 | P1 | 925.7 | Include auth router with /auth prefix |
| **Validate**: register/login/me flow works | 925.10 | P1 | 925.8 | End-to-end test per auth/spec.md scenarios |

---

## Phase 4: Categories Domain
**Epic**: `fastapi-todo-api-beads-ig8`
**Goal**: Category CRUD working (needed before todos)
**Blocked By**: Phase 3 epic

| Task | ID | Priority | Blocked By | Description |
|------|----|----------|------------|-------------|
| Create src/categories/models.py | ig8.7 | P1 | - | Category model with user_id FK, unique name per user |
| Create Alembic migration for category table | ig8.1 | P1 | ig8.7 | Generate and run migration |
| Create src/categories/schemas.py | ig8.2 | P1 | - | CategoryCreate, CategoryUpdate, CategoryResponse |
| Create src/categories/exceptions.py | ig8.3 | P1 | - | CategoryNotFoundError, CategoryExistsError |
| Create src/categories/service.py | ig8.4 | P1 | ig8.2, ig8.3 | CRUD operations |
| Create src/categories/dependencies.py | ig8.5 | P1 | - | get_category_or_404 dependency |
| Create src/categories/router.py | ig8.6 | P1 | ig8.4, ig8.5, 925.6 | Full CRUD endpoints per categories/spec.md |
| Mount categories router in main.py | ig8.8 | P1 | ig8.6 | Include categories router with /categories prefix |
| **Validate**: category CRUD works via API | ig8.9 | P1 | ig8.8 | Test per categories/spec.md scenarios |

---

## Phase 5: Todos Domain
**Epic**: `fastapi-todo-api-beads-jx6`
**Goal**: Todo CRUD with filtering working
**Blocked By**: Phase 4 epic

| Task | ID | Priority | Blocked By | Description |
|------|----|----------|------------|-------------|
| Create src/todos/models.py | jx6.6 | P1 | ig8.7 | Todo model with status enum, priority, due_date, category FK |
| Create Alembic migration for todo table | jx6.1 | P1 | jx6.6 | Generate and run migration |
| Create src/todos/schemas.py | jx6.2 | P1 | - | TodoCreate, TodoUpdate, TodoResponse, TodoFilters |
| Create src/todos/exceptions.py | jx6.3 | P1 | - | TodoNotFoundError |
| Create src/todos/service.py | jx6.4 | P1 | jx6.2, jx6.3 | CRUD and filtering logic |
| Create src/todos/dependencies.py | jx6.5 | P1 | - | get_todo_or_404 dependency |
| Create src/todos/router.py | jx6.8 | P1 | jx6.4, jx6.5, 925.6, ig8.5 | Full CRUD + filtering per todos/spec.md |
| Mount todos router in main.py | jx6.7 | P1 | jx6.8 | Include todos router with /todos prefix |
| **Validate**: todo CRUD and filtering works | jx6.9 | P1 | jx6.7 | Test per todos/spec.md scenarios |

---

## Phase 6: Testing & Validation
**Epic**: `fastapi-todo-api-beads-5og`
**Goal**: Test suite with good coverage and final validation
**Blocked By**: Phase 5 epic

| Task | ID | Priority | Blocked By | Description |
|------|----|----------|------------|-------------|
| Create tests/__init__.py | 5og.8 | P2 | - | Required for pytest package recognition |
| Create tests/conftest.py | 5og.5 | P2 | - | Async fixtures: test db, client, auth helpers |
| Create tests/test_auth.py | 5og.1 | P2 | - | Registration, login, and token tests |
| Create tests/test_categories.py | 5og.2 | P2 | - | CRUD and ownership tests |
| Create tests/test_todos.py | 5og.3 | P2 | - | CRUD, filtering, and category assignment tests |
| Run pytest and ensure all tests pass | 5og.4 | P2 | 5og.5, 5og.1, 5og.2, 5og.3 | Execute `uv run pytest`, fix any failures |
| Run ruff check and fix issues | 5og.7 | P2 | - | Execute `uv run ruff check src tests` |
| Run mypy and fix type errors | 5og.6 | P2 | - | Execute `uv run mypy src` |
| **Verify**: pytest coverage >80% | 5og.9 | P2 | 5og.4 | `uv run pytest --cov=src` meets target |
| **Verify**: all endpoints match spec scenarios | 5og.10 | P2 | 5og.4 | Review implementation against specs |
| **Verify**: /docs shows complete OpenAPI docs | 5og.11 | P2 | 5og.4 | All endpoints documented per spec |

---

## Dependency Graph Summary

### Epic Chain (Sequential)
```
Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6
  (c4s)     (x5l)     (925)     (ig8)     (jx6)     (5og)
```

### Key Cross-Phase Task Dependencies
```
auth/dependencies.py (925.6) ──┬──→ categories/router.py (ig8.6)
                               └──→ todos/router.py (jx6.8)

categories/models.py (ig8.7) ────→ todos/models.py (jx6.6)

categories/dependencies.py (ig8.5) → todos/router.py (jx6.8)
```

### Critical Path (P1)
```
pyproject.toml → uv sync → validate
      ↓
config.py → database.py → dependencies.py
      ↓
exceptions.py → main.py → validate
      ↓
auth/models.py → migration → schemas/exceptions → service → router → mount → validate
      ↓
categories/models.py → migration → schemas/exceptions → service → router → mount → validate
      ↓
todos/models.py → migration → schemas/exceptions → service → router → mount → validate
      ↓
tests → pytest → DoD verification
```

---

## Parallelization Notes

**Can run in parallel within phases**:
- Phase 1: c4s.3, c4s.4, c4s.7, c4s.8 (config files)
- Phase 2: x5l.3, x5l.4 (schemas, exceptions)
- Phase 3-5: schemas.py and exceptions.py within each domain
- Phase 6: 5og.1, 5og.2, 5og.3 (test files), 5og.6, 5og.7 (linting)

**Must be sequential**:
- Each domain: models → migration → service → router → mount
- Cross-domain: auth deps must exist before categories/todos routers
- Categories model must exist before todos model (FK relationship)

---

## Definition of Done

- [ ] All API endpoints match spec scenarios (auth, categories, todos)
- [ ] `uv run pytest` passes with >80% coverage on business logic
- [ ] `uv run ruff check src tests` reports no issues
- [ ] `uv run mypy src` reports no errors
- [ ] `/docs` shows complete OpenAPI documentation
- [ ] `.env.example` documents all required variables
- [ ] README.md provides setup and usage instructions
