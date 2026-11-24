from pydantic import BaseModel, EmailStr, Field
from uuid import UUID

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    organization_name: str = Field(min_length=1, max_length=200)
    display_name: str | None = Field(default=None, max_length=200)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class OrganizationProfile(BaseModel):
    id: UUID
    name: str
    role: str

class UserProfile(BaseModel):
    id: UUID
    email: EmailStr
    display_name: str
    organization: OrganizationProfile

class MessageResponse(BaseModel):
    message: str
