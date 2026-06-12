from typing import Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.entities import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_account(self, account: str) -> Optional[User]:
        return self.db.scalar(
            select(User).where(or_(User.username == account, User.email == account))
        )

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.scalar(select(User).where(User.username == username))

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.scalar(select(User).where(User.email == email))
