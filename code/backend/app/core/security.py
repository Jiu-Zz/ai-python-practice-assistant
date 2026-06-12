import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any, Dict, Optional

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import AuthError, PermissionDeniedError
from app.models.entities import User


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"pbkdf2_sha256${salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt, stored_digest = password_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return hmac.compare_digest(digest.hex(), stored_digest)


def create_access_token(user_id: int, role: str) -> str:
    expires_at = int(time.time()) + settings.access_token_expire_minutes * 60
    payload = {"sub": user_id, "role": role, "exp": expires_at}
    payload_part = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(settings.secret_key.encode("utf-8"), payload_part.encode("utf-8"), hashlib.sha256)
    return f"{payload_part}.{_b64encode(signature.digest())}"


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload_part, signature_part = token.split(".", 1)
    except ValueError:
        raise AuthError("无效的登录凭证")

    expected_signature = hmac.new(
        settings.secret_key.encode("utf-8"),
        payload_part.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(_b64encode(expected_signature), signature_part):
        raise AuthError("无效的登录凭证")

    payload = json.loads(_b64decode(payload_part).decode("utf-8"))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise AuthError("登录已过期，请重新登录")
    return payload


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthError("请先登录")
    token = authorization.replace("Bearer ", "", 1).strip()
    payload = decode_access_token(token)
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise AuthError("用户不存在或已失效")
    return user


def get_optional_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "", 1).strip()
    payload = decode_access_token(token)
    return db.get(User, int(payload["sub"]))


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise PermissionDeniedError()
    return current_user
