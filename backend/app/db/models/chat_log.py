from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String, Text

from app.db.base import Base


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(String, primary_key=True, index=True)  # type: ignore
    user_id = Column(String, index=True, nullable=False)  # type: ignore
    role = Column(String, nullable=False, default="user")  # type: ignore
    content = Column(Text, nullable=False)  # type: ignore
    memori_ref = Column(String, nullable=True)  # type: ignore
    created_at = Column(DateTime, default=datetime.utcnow)  # type: ignore

    def __init__(
        self,
        id: str,
        user_id: str,
        content: str,
        role: str = "user",
        memori_ref: Optional[str] = None,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.content = content
        self.role = role
        self.memori_ref = memori_ref
