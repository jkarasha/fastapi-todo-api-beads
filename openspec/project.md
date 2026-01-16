# Project Context

## Purpose
A production-ready Todo API backend service providing comprehensive task management capabilities. The API supports personal and team task organization with features including user authentication, categorization, and scheduled reminders.

## Tech Stack
- **Framework**: FastAPI (Python 3.13+)
- **Package Management**: uv (fast Python package installer)
- **Database**: SQLite with SQLAlchemy ORM (async via aiosqlite)
- **Migrations**: Alembic with human-readable naming (`YYYY-MM-DD_slug.py`)
- **Authentication**: JWT tokens (python-jose)
- **Validation**: Pydantic v2 for request/response models
- **Password Hashing**: passlib with bcrypt
- **Testing**: pytest with pytest-asyncio, httpx AsyncClient
- **Linting/Formatting**: ruff (replaces black, isort, autoflake)
- **Type Checking**: mypy

## Project Conventions

### Code Style
- Full type annotations on all functions and methods
- Pydantic models for all request/response schemas
- snake_case for variables, functions, and modules
- PascalCase for classes and Pydantic models
- SCREAMING_SNAKE_CASE for constants
- Line length: 88 characters (ruff default)
- Use f-strings for string formatting

### Async Patterns
- Use `async def` for routes with I/O operations (database, external APIs)
- Use regular `def` for CPU-bound or truly synchronous operations
- Never call blocking functions (e.g., `time.sleep()`) in async routes; use `await asyncio.sleep()`
- For sync third-party SDKs, use `await run_in_threadpool(sync_function)`
- Prefer async dependencies over sync to avoid threadpool overhead

### Pydantic Best Practices
- Create a custom `BaseSchema` class for consistent serialization across the app
- Use `Field()` with constraints: `min_length`, `max_length`, `ge`, `le`, `pattern`
- Leverage built-in validators: `EmailStr`, `HttpUrl`, enums
- Serialize datetime fields with explicit timezone handling
- Avoid raising `ValueError` in validators (exposes internals); use custom exceptions

### Architecture Patterns
- **Domain-Organized Structure** (inside `src/`):
  ```
  src/
  ├── auth/           # Authentication domain
  ├── todos/          # Todo management domain
  ├── categories/     # Category domain
  └── core/           # Shared: config, db, dependencies, exceptions
  ```
- **Each domain module contains**:
  - `router.py` - API endpoints
  - `schemas.py` - Pydantic request/response models
  - `models.py` - SQLAlchemy ORM models
  - `service.py` - Business logic
  - `dependencies.py` - Route-specific dependencies
  - `exceptions.py` - Domain-specific errors
  - `constants.py` - Domain constants (optional)
- **Dependency Injection**: Use FastAPI's `Depends()` for DB sessions, auth, and validation
- **Dependencies as Validation**: Use dependencies for DB constraint checks (e.g., resource existence, ownership)
- **Dependency Caching**: FastAPI caches dependency results per-request; reuse freely

### Database Conventions
- snake_case table and column names
- Singular table names (`todo`, `user`, `category`)
- Prefix related tables: `todo_tag`, `todo_reminder`
- Timestamp columns use `_at` suffix: `created_at`, `updated_at`, `completed_at`
- Date columns use `_date` suffix: `due_date`
- Explicit index naming: `ix_<table>_<column>`
- Let the database handle joins and aggregations (SQL-first philosophy)

### Testing Strategy
- Unit tests for service layer business logic
- Integration tests for API endpoints using `httpx.AsyncClient` with `ASGITransport`
- Use pytest fixtures for database setup/teardown
- Test database uses in-memory SQLite (`:memory:`)
- Aim for >80% code coverage on business logic
- Set up async test infrastructure from day one to avoid event loop conflicts

### Error Handling
- Define custom exception classes per domain (e.g., `TodoNotFoundError`, `UnauthorizedError`)
- Use FastAPI exception handlers to convert domain exceptions to HTTP responses
- Consistent error response format:
  ```json
  {"detail": "Error message", "code": "ERROR_CODE"}
  ```
- Never expose internal implementation details in error messages
- Log exceptions with context for debugging

### API Documentation
- Document all endpoints with `response_model`, `status_code`, `description`
- Use `responses` parameter to document multiple possible status codes
- Include request/response examples in schema docstrings
- Consider hiding docs in production (`docs_url=None` if `ENV=production`)

### Configuration Management
- Use Pydantic `BaseSettings` for environment configuration
- Split settings by domain: `AuthSettings`, `DatabaseSettings`, etc.
- Load from `.env` file in development
- Never commit secrets; use environment variables

### Git Workflow
- Main branch: `main` (protected)
- Feature branches: `feature/<description>`
- Bug fixes: `fix/<description>`
- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Squash merge feature branches

## Domain Context
- **Todo**: A task item with title, description, status, due date, and optional category
- **User**: Account with email, hashed password, and owned todos
- **Category**: User-defined groupings for organizing todos (e.g., "Work", "Personal")
- **Status**: Todo states - `pending`, `in_progress`, `completed`
- **Priority**: Optional priority levels (0-4, where 0 is highest)

## Important Constraints
- SQLite for simplicity (single-file database, no external dependencies)
- JWT tokens must expire within 24 hours
- Passwords must be hashed, never stored in plaintext
- Users can only access their own todos and categories
- API responses must be JSON with consistent error format

## External Dependencies
- No external services required (self-contained)
- Future considerations:
  - Email service for reminders/notifications
  - Redis for caching (if scaling needed)
