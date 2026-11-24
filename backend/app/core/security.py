from datetime import UTC, datetime, timedelta
import uuid
import jwt
from pwdlib import PasswordHash
from app.core.config import settings

password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"
ACCESS_TOKEN_SECONDS = 15 * 60
REFRESH_TOKEN_SECONDS = 7 * 24 * 60 * 60

def require_jwt_secret() -> str:
    secret = settings.jwt_secret_key
    if secret is None or len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET_KEY must be configured with at least 32 bytes")
    return secret

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str | None) -> bool:
    if hashed is None:
        password_hash.hash(password)
        return False
    return password_hash.verify(password, hashed)

def create_token(*, user_id: uuid.UUID, organization_id: uuid.UUID, token_type: str, lifetime: int, jti: uuid.UUID | None = None) -> tuple[str, uuid.UUID]:
    now = datetime.now(UTC)
    token_id = jti or uuid.uuid4()
    payload = {"sub": str(user_id), "org": str(organization_id), "jti": str(token_id), "type": token_type, "iat": now, "exp": now + timedelta(seconds=lifetime)}
    return jwt.encode(payload, require_jwt_secret(), algorithm=ALGORITHM), token_id

def decode_token(token: str, expected_type: str) -> dict:
    payload = jwt.decode(token, require_jwt_secret(), algorithms=[ALGORITHM], options={"require": ["sub", "org", "jti", "type", "exp", "iat"]})
    if payload.get("type") != expected_type:
        raise jwt.InvalidTokenError("Unexpected token type")
    return payload
