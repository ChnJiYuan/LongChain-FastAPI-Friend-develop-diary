import contextlib
import logging
from typing import Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db import models  # noqa: F401 - ensure models are registered for metadata

logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create tables if they do not exist; best-effort for dev/bootstrap."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:  # pragma: no cover - init best-effort
        logger.warning("Skipping DB init: %s", exc)


@contextlib.contextmanager
def session_scope() -> Iterator[Optional[object]]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
