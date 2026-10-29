import logging
import uuid
from functools import lru_cache
from io import BytesIO

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from PIL import Image, ImageOps

from web_app.config import settings


logger = logging.getLogger(__name__)

DEFAULT_PROFILE_PIC_LOCAL = "/static/profile_pics/default.jpg"


class ImageStorageError(Exception):
    """Raised when the image storage backend fails."""


@lru_cache(maxsize=4)
def _create_s3_client(
    key_id: str,
    application_key: str,
    endpoint_url: str,
    region: str,
):
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=key_id,
        aws_secret_access_key=application_key,
        region_name=region,
        config=Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "standard"},
        ),
    )


def _get_s3_client():
    if not settings.b2_key_id or not settings.b2_application_key.get_secret_value():
        raise ImageStorageError(
            "Backblaze B2 is not configured: set B2_KEY_ID and B2_APPLICATION_KEY"
        )
    if not settings.b2_bucket or not settings.b2_endpoint_url:
        raise ImageStorageError(
            "Backblaze B2 is not configured: set B2_BUCKET and B2_ENDPOINT_URL"
        )
    if not settings.b2_region:
        raise ImageStorageError(
            "Backblaze B2 is not configured: set B2_REGION (e.g. us-west-004)"
        )
    if not settings.b2_private_bucket and not settings.b2_public_url:
        raise ImageStorageError(
            "Backblaze B2 is not configured: set B2_PUBLIC_URL, or set "
            "B2_PRIVATE_BUCKET=true to use presigned URLs"
        )

    return _create_s3_client(
        settings.b2_key_id,
        settings.b2_application_key.get_secret_value(),
        settings.b2_endpoint_url,
        settings.b2_region,
    )


def _object_key(filename: str) -> str:
    """Add the prefix to legacy filenames that were stored without it."""
    if "/" in filename:
        return filename
    prefix = settings.b2_profile_pics_prefix.strip("/")
    return f"{prefix}/{filename}" if prefix else filename


def _default_profile_pic_key() -> str:
    prefix = settings.b2_profile_pics_prefix.strip("/")
    return f"{prefix}/default.jpg" if prefix else "default.jpg"


def _resolve_url(key: str) -> str | None:
    if not settings.b2_private_bucket:
        base_url = settings.b2_public_url.rstrip("/")
        return f"{base_url}/{key}" if base_url else None

    return _get_s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.b2_bucket, "Key": key},
        ExpiresIn=settings.b2_presigned_url_expires_seconds,
    )


def profile_image_url(filename: str | None) -> str:
    """Return a URL for a profile picture.

    Public buckets use B2_PUBLIC_URL directly. Private buckets use a
    short-lived presigned GET URL. Falls back to the bundled default image
    when no picture is set or B2 is unavailable.
    """
    key = _object_key(filename) if filename else _default_profile_pic_key()

    try:
        url = _resolve_url(key)
    except (BotoCoreError, ClientError, ImageStorageError) as exc:
        logger.warning("Failed to create URL for %s: %s", key, exc)
        url = None

    if url:
        return url
    return f"/media/{key}" if filename else DEFAULT_PROFILE_PIC_LOCAL


def _put_object(key: str, body: bytes) -> None:
    try:
        _get_s3_client().put_object(
            Bucket=settings.b2_bucket,
            Key=key,
            Body=body,
            ContentType="image/jpeg",
            # Private objects must not be cached by shared proxies.
            CacheControl=(
                f"private, max-age={settings.b2_presigned_url_expires_seconds}"
                if settings.b2_private_bucket
                else "public, max-age=31536000, immutable"
            ),
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception(
            "Failed to upload image to B2 (bucket=%s, region=%s, key=%s)",
            settings.b2_bucket,
            settings.b2_region,
            key,
        )
        raise ImageStorageError("Failed to upload image to B2") from exc


def process_profile_image(content: bytes, size=(300, 300)) -> str:
    """Resize an uploaded image and store it in B2. Returns the object key."""
    with Image.open(BytesIO(content)) as original:
        img = ImageOps.exif_transpose(original)
        img = ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)

    prefix = settings.b2_profile_pics_prefix.strip("/")
    key = f"{prefix}/{uuid.uuid4()}.jpg" if prefix else f"{uuid.uuid4()}.jpg"

    _put_object(key, buffer.getvalue())

    return key


def upload_default_profile_image(content: bytes) -> str:
    """Upload the bundled default profile picture to B2. Returns the key."""
    key = _default_profile_pic_key()
    _put_object(key, content)
    return key


def delete_profile_image(filename: str | None) -> None:
    """Delete a profile picture object from B2. No-op for empty values."""
    if not filename:
        return

    try:
        _get_s3_client().delete_object(
            Bucket=settings.b2_bucket,
            Key=_object_key(filename),
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception(
            "Failed to delete profile picture from B2 (bucket=%s, key=%s)",
            settings.b2_bucket,
            filename,
        )
        raise ImageStorageError("Failed to delete profile picture from B2") from exc
