import uuid
from typing import Literal

import boto3
from botocore.client import Config

from app.core.config import settings

UploadKind = Literal["resume", "logo", "verification"]

ALLOWED_TYPES: dict[UploadKind, set[str]] = {
    "resume": {"application/pdf"},
    "logo": {"image/png", "image/jpeg", "image/webp"},
    "verification": {"application/pdf", "image/png", "image/jpeg"},
}

MAX_SIZE: dict[UploadKind, int] = {
    "resume": 5 * 1024 * 1024,
    "logo": 2 * 1024 * 1024,
    "verification": 5 * 1024 * 1024,
}


def get_s3_client():
    kwargs = {
        "service_name": "s3",
        "region_name": settings.aws_region,
        "aws_access_key_id": settings.aws_access_key_id,
        "aws_secret_access_key": settings.aws_secret_access_key,
        "config": Config(signature_version="s3v4"),
    }
    if settings.s3_endpoint_url:
        kwargs["endpoint_url"] = settings.s3_endpoint_url
    return boto3.client(**kwargs)


def validate_upload(kind: UploadKind, content_type: str, size: int) -> None:
    if content_type not in ALLOWED_TYPES[kind]:
        raise ValueError(f"Invalid content type for {kind}")
    if size > MAX_SIZE[kind]:
        raise ValueError(f"File too large for {kind}")


def generate_s3_key(kind: UploadKind, user_id: int, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    return f"{kind}/{user_id}/{uuid.uuid4().hex}.{ext}"


def create_presigned_upload(key: str, content_type: str, expires: int = 3600) -> dict:
    client = get_s3_client()
    return client.generate_presigned_post(
        Bucket=settings.s3_bucket,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=[{"Content-Type": content_type}, ["content-length-range", 1, 5 * 1024 * 1024]],
        ExpiresIn=expires,
    )


def create_presigned_download(key: str, expires: int = 3600) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expires,
    )
