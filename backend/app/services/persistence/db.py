import contextlib
from typing import Iterator, Optional

from app.core.config import settings

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except Exception:  # pragma: no cover - optional dependency
    create_engine = None  # type: ignore
    sessionmaker = None  # type: ignore

engine = create_engine(settings.database_url) if create_engine else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if sessionmaker and engine else None


@contextlib.contextmanager
def session_scope() -> Iterator[Optional[object]]:
    if SessionLocal is None:
        yield None
        return
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
