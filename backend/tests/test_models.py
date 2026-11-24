import uuid
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.base import Base
from app.models import Device, Organization, OrganizationRole, OrganizationUser, User, Vehicle
@pytest.fixture
def db():
 engine=create_engine("sqlite://")
 @event.listens_for(engine,"connect")
 def enable_foreign_keys(conn,record): conn.execute("PRAGMA foreign_keys=ON")
 Base.metadata.create_all(engine)
 with Session(engine) as session: yield session
 Base.metadata.drop_all(engine)
def seed(session):
 org=Organization(name="Acme",slug=f"acme-{uuid.uuid4()}"); user=User(email=f"{uuid.uuid4()}@example.com",display_name="Test")
 session.add_all([org,user]); session.flush(); return org,user
def test_membership_role_and_uuid(db):
 org,user=seed(db); membership=OrganizationUser(organization=org,user=user,role=OrganizationRole.admin); db.add(membership); db.commit()
 assert isinstance(org.id,uuid.UUID) and membership.role is OrganizationRole.admin
def test_registration_unique_per_organization(db):
 a,_=seed(db); b,_=seed(db); db.add_all([Vehicle(organization=a,registration_number="X"),Vehicle(organization=b,registration_number="X")]); db.commit()
def test_device_cannot_link_vehicle_across_organizations(db):
 a,_=seed(db); b,_=seed(db); vehicle=Vehicle(organization=a,registration_number="A"); db.add(vehicle); db.flush(); db.add(Device(organization=b,identifier="D",vehicle=vehicle))
 with pytest.raises(IntegrityError): db.commit()
