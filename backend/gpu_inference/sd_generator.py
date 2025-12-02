"""Stable Diffusion image generation placeholder."""

from pathlib import Path


def load_models(model_dir: str) -> list[str]:
    path = Path(model_dir)
    if not path.exists():
        return []
    return [p.name for p in path.glob("*.safetensors")]


def generate(prompt: str, model_dir: str, steps: int = 20) -> dict:
    return {
        "prompt": prompt,
        "steps": steps,
        "models_found": load_models(model_dir),
        "status": "not_implemented",
    }
