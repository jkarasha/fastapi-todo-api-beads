# Design: Bootstrap Todo API

## Overview
This document captures architectural decisions for the initial Todo API implementation.

## Directory Structure

```
fastapi-todo-api/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic BaseSettings
│   │   ├── database.py         # Async SQLAlchemy engine/session
│   │   ├── dependencies.py     # Shared dependencies (get_db, get_current_user)
│   │   ├── exceptions.py       # Base exception classes
│   │   └── schemas.py          # Shared schemas (BaseSchema, ErrorResponse)
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   ├── todos/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── service.py
│   │   ├── dependencies.py
│   │   └── exceptions.py
│   └── categories/
│       ├── __init__.py
│       ├── router.py
│       ├── schemas.py
│       ├── models.py
│       ├── service.py
│       ├── dependencies.py
│       └── exceptions.py
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures: async client, test db
│   ├── test_auth.py
│   ├── test_todos.py
│   └── test_categories.py
├── pyproject.toml
├── alembic.ini
├── .env.example
└── .gitignore
```

## Key Architectural Decisions

### ADR-1: Domain-Organized Module Structure

**Decision**: Organize code by domain (auth, todos, categories) rather than by layer (routes, services, models).

**Rationale**:
- Co-locates related code for easier navigation
- Enables independent development of features
- Aligns with FastAPI best practices
- Simplifies imports within a domain

**Trade-offs**:
- Cross-domain dependencies require explicit imports
- Shared code must live in `core/`

### ADR-2: Async-First with SQLAlchemy 2.0

**Decision**: Use SQLAlchemy 2.0 async API with aiosqlite.

**Rationale**:
- Native async support without thread pool overhead
- Modern SQLAlchemy patterns (select(), scalars())
- Seamless integration with FastAPI's async handlers

**Implementation**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
engine = create_async_engine("sqlite+aiosqlite:///./app.db")
```

### ADR-3: JWT Authentication with Short-Lived Tokens

**Decision**: Use JWT access tokens with 24-hour expiry. No refresh tokens initially.

**Rationale**:
- Stateless authentication (no server-side session storage)
- Simple implementation for initial version
- 24-hour expiry balances security and UX

**Future consideration**: Add refresh tokens if longer sessions are needed.

### ADR-4: Service Layer for Business Logic

**Decision**: Place all business logic in `service.py`, keep `router.py` thin.

**Rationale**:
- Routers handle HTTP concerns only (parsing, responses)
- Services are testable without HTTP layer
- Clear separation of concerns

**Pattern**:
```python
# router.py - thin, delegates to service
@router.post("/todos")
async def create_todo(data: TodoCreate, db: AsyncSession = Depends(get_db)):
    return await TodoService(db).create(data)

# service.py - contains business logic
class TodoService:
    async def create(self, data: TodoCreate) -> Todo:
        # validation, business rules, persistence
```

### ADR-5: Dependencies for Authorization

**Decision**: Use FastAPI dependencies for ownership validation.

**Rationale**:
- Reusable across endpoints
- Cached per-request (no duplicate queries)
- Clear, declarative authorization

**Pattern**:
```python
async def get_todo_or_404(
    todo_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Todo:
    todo = await TodoService(db).get_by_id(todo_id)
    if not todo or todo.user_id != user.id:
        raise TodoNotFoundError()
    return todo
```

### ADR-6: Custom Exception Hierarchy

**Decision**: Domain exceptions inherit from a base `AppException`, converted to HTTP responses via handlers.

**Rationale**:
- Clean separation between domain errors and HTTP
- Consistent error response format
- Easy to add logging/metrics

**Structure**:
```python
class AppException(Exception):
    code: str
    message: str
    status_code: int = 400

class TodoNotFoundError(AppException):
    code = "TODO_NOT_FOUND"
    message = "Todo not found"
    status_code = 404
```

## Database Schema

### Entity Relationship

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│   user   │──1:N──│   todo   │──N:1──│ category │
└──────────┘       └──────────┘       └──────────┘
                         │
                   user_id (FK)
                   category_id (FK, nullable)
```

### Tables

**user**
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, AUTO |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL |
| created_at | DATETIME | NOT NULL, DEFAULT NOW |

**category**
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, AUTO |
| user_id | INTEGER | FK(user.id), NOT NULL |
| name | VARCHAR(100) | NOT NULL |
| created_at | DATETIME | NOT NULL, DEFAULT NOW |
| UNIQUE(user_id, name) | | |

**todo**
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PK, AUTO |
| user_id | INTEGER | FK(user.id), NOT NULL |
| category_id | INTEGER | FK(category.id), NULL |
| title | VARCHAR(255) | NOT NULL |
| description | TEXT | NULL |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' |
| priority | INTEGER | NULL, CHECK(0-4) |
| due_date | DATE | NULL |
| created_at | DATETIME | NOT NULL |
| updated_at | DATETIME | NOT NULL |
| completed_at | DATETIME | NULL |

## API Endpoints Summary

### Auth (`/auth`)
| Method | Path | Description |
|--------|------|-------------|
| POST | /auth/register | Create new user |
| POST | /auth/login | Get JWT token |
| GET | /auth/me | Get current user |

### Todos (`/todos`)
| Method | Path | Description |
|--------|------|-------------|
| GET | /todos | List user's todos (with filters) |
| POST | /todos | Create todo |
| GET | /todos/{id} | Get todo by ID |
| PATCH | /todos/{id} | Update todo |
| DELETE | /todos/{id} | Delete todo |

### Categories (`/categories`)
| Method | Path | Description |
|--------|------|-------------|
| GET | /categories | List user's categories |
| POST | /categories | Create category |
| GET | /categories/{id} | Get category by ID |
| PATCH | /categories/{id} | Update category |
| DELETE | /categories/{id} | Delete category |

## Security Considerations

1. **Password Storage**: bcrypt with default work factor
2. **JWT Secrets**: Loaded from environment, never committed
3. **SQL Injection**: Prevented by SQLAlchemy parameterized queries
4. **Authorization**: Every endpoint verifies resource ownership
5. **Input Validation**: Pydantic enforces constraints at API boundary
