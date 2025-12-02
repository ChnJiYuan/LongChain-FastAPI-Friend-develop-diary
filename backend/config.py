import os
from dataclasses import dataclass


def _detect_device() -> str:
    try:
        import torch

        if torch.cuda.is_available():
            return f"cuda:{torch.cuda.current_device()}"
        if torch.backends.mps.is_available():  # type: ignore[attr-defined]
            return "mps"
        return "cpu"
    except Exception:
        return "cpu"


@dataclass
class Settings:
    model_name: str = os.getenv("LLM_MODEL", "bert-base-uncased")
    embeddings_model: str = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
    device: str = os.getenv("DEVICE", _detect_device())
    chroma_path: str = os.getenv("CHROMA_PATH", "backend/db/chroma")
    sd_model_dir: str = os.getenv(
        "SD_MODEL_DIR",
        r"D:\UniWorkSpace\WorkPlace4Future\Stable-diffussion\stable-diffusion-webui\models\Stable-diffusion",
    )


settings = Settings()
