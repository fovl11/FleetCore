import re
import unicodedata
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ACCESS_TOKEN_SECONDS, REFRESH_TOKEN_SECONDS, create_token, decode_token, hash_password, require_jwt_secret, verify_password
from app.db.session import get_db
from app.models import Organization, OrganizationRole, OrganizationUser, RefreshSession, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserProfile

router = APIRouter()
bearer = HTTPBearer(auto_error=False)
REFRESH_COOKIE = "fleetcore_refresh"
REFRESH_COOKIE_PATH = "/api/v1/auth"

class Authenticated:
    def __init__(self, user: User, membership: OrganizationUser, organization: Organization):
        self.user, self.membership, self.organization = user, membership, organization

def _ensure_secret() -> None:
    try:
        require_jwt_secret()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication is not configured") from exc

def _unauthorized() -> HTTPException:
    return HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})

def get_current_auth(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)], db: Annotated[Session, Depends(get_db)]) -> Authenticated:
    _ensure_secret()
    if credentials is None:
        raise _unauthorized()
    try:
        claims = decode_token(credentials.credentials, "access")
        user_id, org_id = uuid.UUID(claims["sub"]), uuid.UUID(claims["org"])
    except (jwt.PyJWTError, ValueError, KeyError, TypeError):
        raise _unauthorized()
    row = db.execute(select(User, OrganizationUser, Organization).join(OrganizationUser, OrganizationUser.user_id == User.id).join(Organization, Organization.id == OrganizationUser.organization_id).where(User.id == user_id, User.is_active.is_(True), Organization.id == org_id)).first()
    if row is None:
        raise _unauthorized()
    return Authenticated(*row)

def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(REFRESH_COOKIE, token, max_age=REFRESH_TOKEN_SECONDS, httponly=True, secure=settings.auth_cookie_secure, samesite="strict", path=REFRESH_COOKIE_PATH)

def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(REFRESH_COOKIE, path=REFRESH_COOKIE_PATH, secure=settings.auth_cookie_secure, httponly=True, samesite="strict")

def _issue_tokens(db: Session, user: User, organization: Organization, response: Response) -> TokenResponse:
    refresh, jti = create_token(user_id=user.id, organization_id=organization.id, token_type="refresh", lifetime=REFRESH_TOKEN_SECONDS)
    now = datetime.now(UTC)
    db.add(RefreshSession(jti=jti, user_id=user.id, organization_id=organization.id, expires_at=now + timedelta(seconds=REFRESH_TOKEN_SECONDS)))
    access, _ = create_token(user_id=user.id, organization_id=organization.id, token_type="access", lifetime=ACCESS_TOKEN_SECONDS)
    db.commit()
    _set_refresh_cookie(response, refresh)
    return TokenResponse(access_token=access, expires_in=ACCESS_TOKEN_SECONDS)

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    _ensure_secret()
    email = str(payload.email).strip().lower()
    if db.scalar(select(User.id).where(User.email == email)) is not None:
        raise HTTPException(status_code=409, detail="Email is already registered")
    name = payload.organization_name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Organization name cannot be blank")
    normalized = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    base_slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")[:80] or "organization"
    organization = Organization(name=name, slug=f"{base_slug}-{uuid.uuid4().hex[:8]}")
    user = User(email=email, display_name=(payload.display_name or email.split("@", 1)[0]).strip(), hashed_password=hash_password(payload.password))
    db.add_all([organization, user])
    try:
        db.flush()
        db.add(OrganizationUser(user_id=user.id, organization_id=organization.id, role=OrganizationRole.owner))
        return _issue_tokens(db, user, organization, response)
    except IntegrityError as exc:
        db.rollback()
        if db.scalar(select(User.id).where(User.email == email)) is not None:
            raise HTTPException(status_code=409, detail="Email is already registered") from exc
        raise

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    _ensure_secret()
    email = str(payload.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(payload.password, user.hashed_password) or not user.is_active:
        if user is None:
            verify_password(payload.password, None)
        raise _unauthorized()
    row = db.execute(select(OrganizationUser, Organization).join(Organization, Organization.id == OrganizationUser.organization_id).where(OrganizationUser.user_id == user.id).order_by(OrganizationUser.created_at).limit(1)).first()
    if row is None:
        raise _unauthorized()
    return _issue_tokens(db, user, row[1], response)

@router.post("/refresh", response_model=TokenResponse)
def refresh(response: Response, db: Annotated[Session, Depends(get_db)], refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None) -> TokenResponse:
    _ensure_secret()
    if refresh_token is None:
        raise _unauthorized()
    try:
        claims = decode_token(refresh_token, "refresh")
        jti, user_id, org_id = uuid.UUID(claims["jti"]), uuid.UUID(claims["sub"]), uuid.UUID(claims["org"])
    except (jwt.PyJWTError, ValueError, KeyError, TypeError):
        raise _unauthorized()
    session = db.scalar(select(RefreshSession).where(RefreshSession.jti == jti).with_for_update())
    if session is None or session.revoked_at is not None or session.user_id != user_id or session.organization_id != org_id:
        raise _unauthorized()
    row = db.execute(select(User, OrganizationUser, Organization).join(OrganizationUser, OrganizationUser.user_id == User.id).join(Organization, Organization.id == OrganizationUser.organization_id).where(User.id == user_id, User.is_active.is_(True), Organization.id == org_id)).first()
    if row is None:
        raise _unauthorized()
    session.revoked_at = datetime.now(UTC)
    try:
        return _issue_tokens(db, row[0], row[2], response)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Could not rotate refresh token") from exc

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, db: Annotated[Session, Depends(get_db)], refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None) -> Response:
    if refresh_token:
        try:
            claims = decode_token(refresh_token, "refresh")
            session = db.get(RefreshSession, uuid.UUID(claims["jti"]))
            if session is not None and session.revoked_at is None:
                session.revoked_at = datetime.now(UTC)
                db.commit()
        except (jwt.PyJWTError, RuntimeError, ValueError, KeyError, TypeError):
            db.rollback()
    _clear_refresh_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response

@router.get("/me", response_model=UserProfile)
def me(current: Annotated[Authenticated, Depends(get_current_auth)]) -> UserProfile:
    return UserProfile(id=current.user.id, email=current.user.email, display_name=current.user.display_name, organization={"id": current.organization.id, "name": current.organization.name, "role": current.membership.role.value})

def require_roles(*roles: OrganizationRole):
    def check(current: Annotated[Authenticated, Depends(get_current_auth)]) -> Authenticated:
        if current.membership.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient organization role")
        return current
    return check
