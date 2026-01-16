# Proposal: Bootstrap Todo API

## Change ID
`bootstrap-api`

## Summary
Initialize the FastAPI Todo API project with complete foundational infrastructure and core functionality. This greenfield implementation establishes the domain-organized architecture, authentication system, todo management, and category organization as defined in `openspec/project.md`.

## Motivation
This is a new project requiring a production-ready Todo API backend. The implementation needs:
- Secure user authentication with JWT tokens
- Full CRUD operations for todos with due dates and priorities
- Category-based organization for todos
- Async-first architecture with SQLite persistence
- Comprehensive test infrastructure

## Scope

### In Scope
- Project scaffolding with uv, pyproject.toml, and dev tooling
- Core infrastructure: async database, configuration, error handling
- User authentication: registration, login, JWT token management
- Todo CRUD: create, read, update, delete with filtering
- Category management: user-scoped categories for organizing todos
- Alembic migrations for database schema
- Test infrastructure with pytest-asyncio and httpx

### Out of Scope
- Email notifications/reminders (future consideration)
- Redis caching (future consideration)
- Rate limiting
- API versioning
- Admin interface

## Capabilities

| Capability | Description | Dependencies |
|------------|-------------|--------------|
| `core-infrastructure` | Project setup, config, database, error handling | None |
| `auth` | User registration, login, JWT authentication | core-infrastructure |
| `categories` | Category CRUD for organizing todos | core-infrastructure, auth |
| `todos` | Todo CRUD with status, priority, due dates | core-infrastructure, auth, categories |

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SQLite concurrency limits | Medium | Acceptable for initial scope; document PostgreSQL migration path |
| JWT token security | High | Use short expiry (24h), secure secret key management |
| Async complexity | Low | Follow established patterns from project.md |

## Success Criteria
- All API endpoints return correct responses per spec
- Authentication flow works end-to-end
- Tests pass with >80% coverage on business logic
- `ruff check` and `mypy` pass without errors
- API documentation auto-generated at `/docs`
