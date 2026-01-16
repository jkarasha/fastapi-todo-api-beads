from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.auth.schemas import UserCreate
from src.auth.service import AuthService, create_access_token
from src.core.database import Base, get_db
from src.main import app

# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_async_session = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession]:
    """Create a fresh database for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_async_session() as session:
        yield session
        await session.rollback()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient]:
    """Create an async test client with database override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(db: AsyncSession) -> dict[str, str]:
    """Create a test user and return auth headers."""
    user_data = UserCreate(email="test@example.com", password="testpassword123")
    user = await AuthService(db).create_user(user_data)
    await db.commit()
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def second_user_headers(db: AsyncSession) -> dict[str, str]:
    """Create a second test user and return auth headers."""
    user_data = UserCreate(email="other@example.com", password="testpassword123")
    user = await AuthService(db).create_user(user_data)
    await db.commit()
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}
