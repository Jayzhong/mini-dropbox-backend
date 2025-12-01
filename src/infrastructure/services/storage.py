import asyncio
from typing import BinaryIO
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from src.infrastructure.config.settings import settings
from src.application.files.interfaces import StorageService

class S3StorageService(StorageService):
    """
    Implementation of StorageService using boto3 wrapped in asyncio.to_thread
    for compatibility with async call sites. This avoids aioboto3 hanging issues
    seen against local MinIO.
    """
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self._client = self._build_client()

    def _build_client(self):
        # Short timeouts + path-style to keep local MinIO calls snappy in tests
        config = Config(
            connect_timeout=3,
            read_timeout=3,
            retries={"max_attempts": 1},
            s3={"addressing_style": "path"},
        )
        return boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=config,
        )

    async def upload_file(self, key: str, data: BinaryIO, content_type: str) -> None:
        """Uploads by buffering to bytes and issuing a synchronous put_object in a thread."""
        try:
            if hasattr(data, "seek"):
                data.seek(0)
            body = data.read()

            def _put():
                self._client.put_object(
                    Bucket=self.bucket_name,
                    Key=key,
                    Body=body,
                    ContentType=content_type,
                )

            await asyncio.to_thread(_put)
        except ClientError as e:
            # TODO: replace with structured logging
            print(f"S3 ClientError during upload: {e}")
            raise e

    async def download_file(self, key: str) -> str:
        try:
            def _presign():
                return self._client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": key},
                    ExpiresIn=3600,  # URL valid for 1 hour
                )

            return await asyncio.to_thread(_presign)
        except ClientError as e:
            # TODO: Log error
            raise e

    async def delete_file(self, key: str) -> None:
        try:
            await asyncio.to_thread(self._client.delete_object, Bucket=self.bucket_name, Key=key)
        except ClientError as e:
            # TODO: Log error
            raise e
