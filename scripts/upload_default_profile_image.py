#!/usr/bin/env python3
"""Upload the bundled default profile picture to Backblaze B2.

Usage (from the repository root):
    uv run python scripts/upload_default_profile_image.py
"""

from pathlib import Path

from web_app.config import settings
from web_app.image_utils import (
    DEFAULT_PROFILE_PIC_LOCAL,
    profile_image_url,
    upload_default_profile_image,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
LOCAL_PATH = ROOT_DIR / DEFAULT_PROFILE_PIC_LOCAL.lstrip("/")


def main() -> None:
    if not LOCAL_PATH.is_file():
        raise SystemExit(f"Default image not found: {LOCAL_PATH}")

    key = upload_default_profile_image(LOCAL_PATH.read_bytes())
    print(f"Uploaded {LOCAL_PATH} -> b2://{settings.b2_bucket}/{key}")
    print(f"URL: {profile_image_url(None)}")


if __name__ == "__main__":
    main()
