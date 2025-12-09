from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, String

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)  # type: ignore
    name = Column(String, nullable=True)  # type: ignore
    created_at = Column(DateTime, default=datetime.utcnow)  # type: ignore

    def __init__(self, user_id: str, name: Optional[str] = None) -> None:
        self.user_id = user_id
        self.name = name
