import logging
from logging.config import dictConfig


def configure_logging(level: str = "INFO") -> None:
    """Configure simple structured logging once at startup."""
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
                }
            },
            "handlers": {
                "default": {
                    "level": level,
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                }
            },
            "root": {"handlers": ["default"], "level": level},
        }
    )
    logging.getLogger(__name__).debug("Logging configured at %s", level)


__all__ = ["configure_logging"]
