import enum
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, ForeignKeyConstraint, String, UniqueConstraint, Uuid, and_, func
from sqlalchemy.orm import Mapped, foreign, mapped_column, relationship
from app.db.base import Base

class Identity:
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class Organization(Identity, Base):
    __tablename__ = "organizations"
    __table_args__ = (UniqueConstraint("slug", name="uq_organizations_slug"),)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    memberships: Mapped[list["OrganizationUser"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    vehicles: Mapped[list["Vehicle"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    devices: Mapped[list["Device"]] = relationship(back_populates="organization", cascade="all, delete-orphan")

class User(Identity, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    memberships: Mapped[list["OrganizationUser"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    refresh_sessions: Mapped[list["RefreshSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class OrganizationRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    manager = "manager"
    viewer = "viewer"

class OrganizationUser(Identity, Base):
    __tablename__ = "organization_users"
    __table_args__ = (UniqueConstraint("organization_id", "user_id", name="uq_org_user_membership"),)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[OrganizationRole] = mapped_column(Enum(OrganizationRole, name="organization_role"), default=OrganizationRole.manager, server_default="manager", nullable=False)
    organization: Mapped[Organization] = relationship(back_populates="memberships")
    user: Mapped[User] = relationship(back_populates="memberships")

class Vehicle(Identity, Base):
    __tablename__ = "vehicles"
    __table_args__ = (UniqueConstraint("organization_id", "id", name="uq_vehicle_org_id"), UniqueConstraint("organization_id", "registration_number", name="uq_vehicle_org_registration"))
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    registration_number: Mapped[str] = mapped_column(String(40), nullable=False)
    make: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    organization: Mapped[Organization] = relationship(back_populates="vehicles")
    devices: Mapped[list["Device"]] = relationship(primaryjoin=lambda: and_(Vehicle.id == foreign(Device.vehicle_id), Vehicle.organization_id == Device.organization_id), foreign_keys=lambda: [Device.vehicle_id], back_populates="vehicle")

class Device(Identity, Base):
    __tablename__ = "devices"
    __table_args__ = (UniqueConstraint("organization_id", "id", name="uq_device_org_id"), UniqueConstraint("organization_id", "identifier", name="uq_device_org_identifier"), ForeignKeyConstraint(["organization_id", "vehicle_id"], ["vehicles.organization_id", "vehicles.id"], name="fk_device_vehicle_same_org", ondelete="CASCADE"))
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    identifier: Mapped[str] = mapped_column(String(100), nullable=False)
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    organization: Mapped[Organization] = relationship(back_populates="devices")
    vehicle: Mapped[Vehicle | None] = relationship(primaryjoin=lambda: and_(Vehicle.id == foreign(Device.vehicle_id), Vehicle.organization_id == Device.organization_id), foreign_keys=lambda: [Device.vehicle_id], back_populates="devices")

class RefreshSession(Base):
    __tablename__ = "auth_refresh_sessions"
    jti: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user: Mapped[User] = relationship(back_populates="refresh_sessions")
