import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine

from src.infrastructure.config.settings import settings
from src.interfaces.api.main import app
from src.infrastructure.database.main import get_db_session

TEST_DATABASE_URL = settings.DATABASE_URL

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    # Use the default policy to create a new event loop for the session.
    # This loop will be used by pytest-asyncio for all tests in this session.
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    # Set the created loop as the current loop for the duration of the fixture.
    # This ensures consistency for async operations that implicitly rely on get_event_loop().
    policy.set_event_loop(loop)
    yield loop
    loop.close()
    # Restore the default event loop policy after the session
    policy.set_event_loop_policy(None)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    # Create the engine and sessionmaker *within* the function scope
    # to ensure they are tied to the current test's event loop.
    engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
    SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Establish a connection for the test function
    async with engine.connect() as connection:
        # Begin a transaction that is rolled back after each test
        async with connection.begin() as transaction:
            # Bind a session to this connection and transaction
            async with SessionLocal(bind=connection) as session:
                # Override the app's dependency to use this test session
                app.dependency_overrides[get_db_session] = lambda: session
                try:
                    yield session
                finally:
                    # Rollback the transaction to clean up test data
                    await transaction.rollback()
                    # Clear overrides
                    app.dependency_overrides.clear()
    await engine.dispose() # Dispose engine resources after each test function

@pytest.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]: # db_session implicitly sets up overrides
    """
    Fixture that provides an httpx AsyncClient for the FastAPI app.
    It implicitly uses the overridden db_session.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client