from typing import Optional

from app.db.base import Base

if Base:
    from sqlalchemy import Column, String


class ChatLog(Base) if Base else object:  # type: ignore
    __tablename__ = "chat_logs"

    if Base:
        id = Column(String, primary_key=True, index=True)  # type: ignore
        user_id = Column(String, index=True)  # type: ignore
        content = Column(String)  # type: ignore

    def __init__(self, id: str, user_id: str, content: str) -> None:
        self.id = id
        self.user_id = user_id
        self.content = content
