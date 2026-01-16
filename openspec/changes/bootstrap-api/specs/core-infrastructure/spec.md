# Capability: Core Infrastructure

## Overview
Foundational project setup including configuration management, async database connectivity, shared schemas, and error handling infrastructure.

## ADDED Requirements

### Requirement: Project Scaffolding
The project MUST have a properly configured Python package with uv and development tooling.

#### Scenario: Project initialization
- **Given** a new project directory
- **When** the project is initialized
- **Then** `pyproject.toml` exists with FastAPI, SQLAlchemy, and dev dependencies
- **And** `uv.lock` exists with pinned versions
- **And** `ruff.toml` configures linting (line-length=88)
- **And** `.gitignore` excludes `.venv`, `__pycache__`, `.env`, `*.db`
- **And** `.env.example` documents required environment variables

#### Scenario: Development environment setup
- **Given** the project is cloned
- **When** `uv sync` is run
- **Then** all dependencies are installed in `.venv`
- **And** `uv run ruff check src` executes without error
- **And** `uv run mypy src` executes without error

---

### Requirement: Configuration Management
Application configuration MUST be loaded from environment variables using Pydantic BaseSettings.

#### Scenario: Loading configuration
- **Given** environment variables are set (or `.env` file exists)
- **When** the application starts
- **Then** `Settings` object is populated with:
  - `DATABASE_URL` (default: `sqlite+aiosqlite:///./app.db`)
  - `SECRET_KEY` (required, no default)
  - `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 1440 = 24 hours)
  - `ENV` (default: `development`)

#### Scenario: Missing required configuration
- **Given** `SECRET_KEY` is not set
- **When** the application starts
- **Then** application fails with a clear validation error

---

### Requirement: Async Database Connection
The application MUST provide async database connectivity using SQLAlchemy 2.0.

#### Scenario: Database session management
- **Given** the application is running
- **When** an endpoint needs database access
- **Then** `get_db` dependency provides an `AsyncSession`
- **And** the session is automatically closed after the request
- **And** transactions are committed on success or rolled back on error

#### Scenario: Database initialization
- **Given** the application starts for the first time
- **When** Alembic migrations are run
- **Then** all tables are created in the SQLite database
- **And** migration history is tracked in `alembic_version` table

---

### Requirement: Base Schema Classes
Shared Pydantic schemas MUST provide consistent serialization behavior.

#### Scenario: BaseSchema configuration
- **Given** a schema inherits from `BaseSchema`
- **When** the schema is serialized
- **Then** `from_attributes=True` enables ORM mode
- **And** datetime fields use ISO 8601 format with timezone

---

### Requirement: Error Handling Infrastructure
The application MUST have a consistent error response format and exception handling.

#### Scenario: Domain exception handling
- **Given** a domain exception (e.g., `TodoNotFoundError`) is raised
- **When** the exception reaches FastAPI
- **Then** it is converted to JSON response: `{"detail": "...", "code": "..."}`
- **And** the HTTP status code matches the exception's `status_code`

#### Scenario: Validation error handling
- **Given** a request fails Pydantic validation
- **When** the validation error is returned
- **Then** response format is `{"detail": [...], "code": "VALIDATION_ERROR"}`
- **And** HTTP status is 422

#### Scenario: Unhandled exception
- **Given** an unexpected exception occurs
- **When** the exception is caught by global handler
- **Then** response is `{"detail": "Internal server error", "code": "INTERNAL_ERROR"}`
- **And** HTTP status is 500
- **And** exception is logged with full traceback

---

### Requirement: Application Entry Point
The FastAPI application MUST be properly configured with routers and middleware.

#### Scenario: Application startup
- **Given** the application is started with `uvicorn src.main:app`
- **When** the server is ready
- **Then** `/docs` serves OpenAPI documentation
- **And** `/health` returns `{"status": "ok"}`
- **And** all domain routers are mounted at their prefixes

## Dependencies
None (this is the foundational capability)

## Related Capabilities
- `auth` - depends on database and config
- `todos` - depends on database and schemas
- `categories` - depends on database and schemas
