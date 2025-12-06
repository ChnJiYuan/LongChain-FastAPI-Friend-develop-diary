try:
    from sqlalchemy.orm import declarative_base
except Exception:  # pragma: no cover - optional dependency
    declarative_base = None  # type: ignore

Base = declarative_base() if declarative_base else None

__all__ = ["Base"]
