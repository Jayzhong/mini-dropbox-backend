import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.infrastructure.config.settings import settings
from src.interfaces.api.main import app
from src.infrastructure.database.models.base import Base

# Use the existing settings but ensure we point to the test/dev DB
# For a real pipeline, we might override settings.DATABASE_URL here to point to a separate test DB.
TEST_DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fixture that provides an async session for DB operations within tests.
    This can be used to inspect the DB state or clean up data.
    """
    async with TestingSessionLocal() as session:
        yield session
        # Optional: Rollback if we were using a transaction-per-test strategy
        # But since the API commits, we might need manual cleanup or nested transactions.
        await session.close()

@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that provides an httpx AsyncClient for the FastAPI app.
    """
    # We use ASGITransport to test the app directly without spinning up a server port
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
