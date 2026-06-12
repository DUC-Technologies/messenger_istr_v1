import uuid
from typing import AsyncGenerator

import aioboto3
from botocore.exceptions import ClientError

import settings


class S3StorageService:
    def __init__(self, session: aioboto3.Session):
        self._session = session

    async def upload_file(
        self,
        bucket: str,
        object_key: str,
        file_bytes: bytes,
        content_type: str,
    ) -> None:
        async with self._session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        ) as client:
            await client.put_object(
                Bucket=bucket,
                Key=object_key,
                Body=file_bytes,
                ContentType=content_type,
            )

    async def generate_presigned_url(
        self,
        bucket: str,
        object_key: str,
        expires_in: int = 3600,
    ) -> str:
        async with self._session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        ) as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": object_key},
                ExpiresIn=expires_in,
            )

    async def ensure_bucket_exists(self, bucket: str) -> None:
        async with self._session.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        ) as client:
            try:
                await client.head_bucket(Bucket=bucket)
            except ClientError:
                await client.create_bucket(Bucket=bucket)


def make_report_object_key(user_id: uuid.UUID) -> str:
    return f"reports/{user_id}/{uuid.uuid4()}.pdf"