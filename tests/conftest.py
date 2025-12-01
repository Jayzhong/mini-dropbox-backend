import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine
import aioboto3
from botocore.exceptions import ClientError
from botocore.config import Config

from src.infrastructure.config.settings import settings
from src.interfaces.api.main import app
from src.infrastructure.database.main import get_db_session

TEST_DATABASE_URL = settings.DATABASE_URL

@pytest.fixture(scope="session", autouse=True)
def setup_s3_bucket():
    """
    Fixture to ensure the S3 bucket exists before running tests.
    Uses synchronous boto3 to avoid event loop issues during session setup.
    """
    import boto3
    print(f"\n[Setup] START: Connecting to MinIO at {settings.S3_ENDPOINT_URL} (Sync)...")
    
    # Configure short timeout for tests AND path-style addressing
    config = Config(
        connect_timeout=2,
        read_timeout=2,
        retries={'max_attempts': 1},
        s3={'addressing_style': 'path'}
    )

    s3 = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=config
    )

    try:
        print(f"[Setup] Calling head_bucket for '{settings.S3_BUCKET_NAME}'...")
        s3.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        print(f"[Setup] Bucket '{settings.S3_BUCKET_NAME}' exists.")
    except ClientError as e:
        print(f"[Setup] ClientError caught: {e}")
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "404":
            print(f"[Setup] Bucket '{settings.S3_BUCKET_NAME}' not found. Creating...")
            s3.create_bucket(Bucket=settings.S3_BUCKET_NAME)
            print(f"[Setup] Bucket '{settings.S3_BUCKET_NAME}' created.")
        else:
            print(f"[Setup] Error connecting to S3: {e}")
            raise
    print("[Setup] DONE: S3 setup complete.\n")

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Function-scoped database session. Creates engine per test to avoid event loop issues.
    """
    # Create engine per function to bind to the current event loop
    engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
    SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

    async with engine.connect() as connection:
        async with connection.begin() as transaction:
            async with SessionLocal(bind=connection) as session:
                app.dependency_overrides[get_db_session] = lambda: session
                try:
                    yield session
                finally:
                    await transaction.rollback()
                    app.dependency_overrides.clear()
    
    # Dispose engine to close connections attached to the loop
    await engine.dispose()

@pytest.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]: 
    """
    Fixture that provides an httpx AsyncClient for the FastAPI app.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client