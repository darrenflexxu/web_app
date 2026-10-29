import uuid
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps


PROFILE_PICS_DIR = Path("media/profile_pics")


def process_profile_image(content: bytes, size=(300, 300)) -> str:
    with Image.open(BytesIO(content)) as origial:
        img = ImageOps.exif_transpose(origial)
        img = ImageOps.fit(img, size, method=Image.Resampling.LANCZOS)
        
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        filename = f"{uuid.uuid4()}.jpg"
        filepath = PROFILE_PICS_DIR / filename
        
        PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)
        img.save(filepath, format="JPEG", quality=85, optimize=True)
        
    return filename


def delete_profile_image(filename: str | None) -> None:
    if filename is None:
        return
    filepath = PROFILE_PICS_DIR / filename
    if filepath.exists():
        filepath.unlink()