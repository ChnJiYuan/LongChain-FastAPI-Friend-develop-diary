import base64
from pathlib import Path
from typing import Optional


def save_base64_image(image_b64: str, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(base64.b64decode(image_b64))
    return dest


def validate_image_size(image_b64: str, max_bytes: int = 5 * 1024 * 1024) -> None:
    data_len = len(image_b64.encode("utf-8"))
    if data_len > max_bytes:
        raise ValueError("Image exceeds max size")


def compress_if_needed(image_path: Path, target_size_kb: int = 512) -> Optional[Path]:
    """Placeholder that simply returns the same path; hook real compression later."""
    if image_path.stat().st_size / 1024 <= target_size_kb:
        return image_path
    return image_path
