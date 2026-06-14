import pytest
from httpx import AsyncClient

from app.core.s3 import ALLOWED_TYPES, MAX_SIZE, validate_upload


def test_upload_validation_rejects_bad_mime():
    with pytest.raises(ValueError):
        validate_upload("resume", "application/exe", 1000)


def test_upload_validation_rejects_oversized():
    with pytest.raises(ValueError):
        validate_upload("logo", "image/png", MAX_SIZE["logo"] + 1)


def test_upload_validation_accepts_valid():
    validate_upload("resume", "application/pdf", 1024)
    assert "application/pdf" in ALLOWED_TYPES["resume"]


@pytest.mark.asyncio
async def test_unauthenticated_cannot_access_student_profile(client: AsyncClient):
    response = await client.get("/api/v1/students/me")
    assert response.status_code == 401
