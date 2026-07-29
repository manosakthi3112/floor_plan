import os
import shutil
from pathlib import Path
from uuid import uuid4

from app.config import settings


class StorageBackend:
    async def save(self, file_data: bytes, filename: str) -> str:
        raise NotImplementedError

    async def get_url(self, path: str) -> str:
        raise NotImplementedError

    async def delete(self, path: str) -> None:
        raise NotImplementedError


class LocalStorage(StorageBackend):
    def __init__(self):
        self.base_path = Path(settings.storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save(self, file_data: bytes, filename: str) -> str:
        ext = Path(filename).suffix or '.bin'
        key = f"{uuid4()}{ext}"
        filepath = self.base_path / key
        filepath.write_bytes(file_data)
        return str(filepath)

    async def get_url(self, path: str) -> str:
        return f"/static/uploads/{Path(path).name}"

    async def delete(self, path: str) -> None:
        p = Path(path)
        if p.exists():
            p.unlink()


class S3Storage(StorageBackend):
    def __init__(self):
        import boto3
        self.client = boto3.client(
            's3',
            region_name=settings.s3_region,
        )
        self.bucket = settings.s3_bucket

    async def save(self, file_data: bytes, filename: str) -> str:
        ext = Path(filename).suffix or '.bin'
        key = f"uploads/{uuid4()}{ext}"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=file_data)
        return key

    async def get_url(self, path: str) -> str:
        return f"https://{self.bucket}.s3.{settings.s3_region}.amazonaws.com/{path}"

    async def delete(self, path: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=path)


def get_storage() -> StorageBackend:
    if settings.storage_backend == 's3':
        return S3Storage()
    return LocalStorage()


storage = get_storage()
