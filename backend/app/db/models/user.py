from typing import Optional

from app.db.base import Base

if Base:
    from sqlalchemy import Column, String


class User(Base) if Base else object:  # type: ignore
    __tablename__ = "users"

    if Base:
        user_id = Column(String, primary_key=True, index=True)  # type: ignore
        name = Column(String, nullable=True)  # type: ignore

    def __init__(self, user_id: str, name: Optional[str] = None) -> None:
        self.user_id = user_id
        self.name = name
