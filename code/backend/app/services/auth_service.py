from sqlalchemy.orm import Session

from app.core.errors import AppError, AuthError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.entities import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import LoginRequest, ProfileUpdate, RegisterRequest


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: RegisterRequest) -> dict:
        if self.users.get_by_username(payload.username):
            raise AppError("用户名已存在")
        if self.users.get_by_email(payload.email):
            raise AppError("邮箱已被注册")

        user = User(
            username=payload.username,
            email=payload.email,
            nickname=payload.nickname,
            password_hash=hash_password(payload.password),
            learning_stage=payload.learning_stage,
            role="student",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._auth_payload(user)

    def login(self, payload: LoginRequest) -> dict:
        user = self.users.get_by_account(payload.account)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise AuthError("账号或密码错误")
        return self._auth_payload(user)

    def update_profile(self, user: User, payload: ProfileUpdate) -> User:
        if payload.learning_stage is not None:
            user.learning_stage = payload.learning_stage
        if payload.nickname is not None:
            user.nickname = payload.nickname
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _auth_payload(self, user: User) -> dict:
        token = create_access_token(user.id, user.role)
        return {
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "nickname": user.nickname,
                "role": user.role,
                "learning_stage": user.learning_stage,
            },
        }
