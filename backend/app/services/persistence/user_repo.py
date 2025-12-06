from typing import Any, Dict, Optional


class UserRepo:
    """Placeholder for user persistence."""

    def __init__(self, session: Optional[object]) -> None:
        self.session = session

    def get_user(self, user_id: str) -> Dict[str, Any]:
        return {"user_id": user_id, "note": "not persisted yet"}
