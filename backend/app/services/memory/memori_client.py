import logging
from typing import Any, Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:  # pragma: no cover - import guarded for environments without SDK
    from memori import Memori
except ImportError:  # pragma: no cover
    Memori = None

logger = logging.getLogger(__name__)


FALLBACK_PROFILE = "No profile stored yet."
FALLBACK_FACTS = "No recent facts."


class MemoriClient:
    """Thin wrapper around the Memori SDK with graceful fallback when SDK/unavailable."""

    def __init__(
        self,
        project_id: str,
        api_key: str,
        endpoint: str,
        storage_url: Optional[str] = None,
        openai_api_key: Optional[str] = None,
    ) -> None:
        self.project_id = project_id
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")
        self.storage_url = storage_url
        self.openai_api_key = openai_api_key
        self._client = self._build_client()

    def _build_client(self) -> Optional["Memori"]:
        if Memori is None:
            logger.warning("Memori SDK not installed; MemoriClient will operate in fallback mode.")
            return None
        if not self.api_key:
            logger.warning("Memori API key missing; MemoriClient will operate in fallback mode.")
            return None

        kwargs: Dict[str, Any] = {
            "project_id": self.project_id,
            "api_key": self.api_key,
            "endpoint": self.endpoint,
        }

        if self.storage_url:
            engine = create_engine(self.storage_url)
            SessionLocal = sessionmaker(bind=engine)
            kwargs["conn"] = SessionLocal

        try:
            client = Memori(**kwargs)
        except TypeError as exc:  # pragma: no cover - sdk signature mismatch
            logger.warning("Memori SDK signature mismatch, running in fallback mode: %s", exc)
            return None

        # Optional: register OpenAI client if provided (enables Memori-managed embeddings/LLM)
        if self.openai_api_key and hasattr(client, "openai"):
            try:  # pragma: no cover - optional integration
                from openai import OpenAI

                oa_client = OpenAI(api_key=self.openai_api_key)
                client.openai.register(oa_client)
            except Exception as exc:
                logger.warning("Failed to register OpenAI client with Memori: %s", exc)

        return client

    def save_note(self, user_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        logger.debug(
            "Memori save_note user=%s project=%s metadata=%s",
            user_id,
            self.project_id,
            metadata or {},
        )
        if not self._client:
            return
        try:
            # memori.save(user_id, text, metadata=dict)
            self._client.save(user_id, content, metadata=metadata or {})
        except Exception as exc:  # pragma: no cover - network/SDK failure
            logger.warning("Memori save_note failed: %s", exc)

    def query_profile(self, user_id: str) -> str:
        logger.debug("Memori query_profile user=%s", user_id)
        if not self._client:
            return FALLBACK_PROFILE
        try:
            result = self._client.query(user_id, "basic profile and long-term preferences")
            return self._stringify(result, fallback=FALLBACK_PROFILE)
        except Exception as exc:  # pragma: no cover
            logger.warning("Memori query_profile failed: %s", exc)
            return FALLBACK_PROFILE

    def query_recent_facts(self, user_id: str) -> str:
        logger.debug("Memori query_recent_facts user=%s", user_id)
        if not self._client:
            return FALLBACK_FACTS
        try:
            result = self._client.query(user_id, "recent important events")
            return self._stringify(result, fallback=FALLBACK_FACTS)
        except Exception as exc:  # pragma: no cover
            logger.warning("Memori query_recent_facts failed: %s", exc)
            return FALLBACK_FACTS

    def reset_user(self, user_id: str) -> None:
        logger.debug("Memori reset_user user=%s", user_id)
        if not self._client:
            return
        try:
            if hasattr(self._client, "reset"):
                self._client.reset(user_id)
        except Exception as exc:  # pragma: no cover
            logger.warning("Memori reset_user failed: %s", exc)

    @staticmethod
    def _stringify(result: Any, fallback: str) -> str:
        if result is None:
            return fallback
        if isinstance(result, str):
            return result
        if isinstance(result, (list, tuple)):
            return "\n".join([str(item) for item in result]) or fallback
        if isinstance(result, dict):
            return "\n".join(f"{k}: {v}" for k, v in result.items()) or fallback
        return str(result)
