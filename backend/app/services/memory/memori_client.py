import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class MemoriClient:
    """Thin wrapper around the Memori SDK (placeholder implementation)."""

    def __init__(self, project_id: str, api_key: str, endpoint: str) -> None:
        self.project_id = project_id
        self.api_key = api_key
        self.endpoint = endpoint.rstrip("/")

    def save_note(self, user_id: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        logger.debug(
            "Memori save_note user=%s project=%s metadata=%s",
            user_id,
            self.project_id,
            metadata or {},
        )
        # TODO: replace with real Memori SDK call

    def query_profile(self, user_id: str) -> str:
        logger.debug("Memori query_profile user=%s", user_id)
        return "No profile stored yet."  # placeholder

    def query_recent_facts(self, user_id: str) -> str:
        logger.debug("Memori query_recent_facts user=%s", user_id)
        return "No recent facts."  # placeholder

    def reset_user(self, user_id: str) -> None:
        logger.debug("Memori reset_user user=%s", user_id)
        # TODO: implement Memori user reset
