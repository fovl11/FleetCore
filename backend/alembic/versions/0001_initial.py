"""Initial organization and fleet schema."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0001_initial"
down_revision=None
branch_labels=None
depends_on=None
def upgrade():
 op.create_table("organizations",sa.Column("name",sa.String(200),nullable=False),sa.Column("slug",sa.String(100),nullable=False),sa.Column("id",sa.Uuid(),primary_key=True),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()"),nullable=False),sa.UniqueConstraint("slug",name="uq_organizations_slug"))
 op.create_table("users",sa.Column("email",sa.String(320),nullable=False),sa.Column("display_name",sa.String(200),nullable=False),sa.Column("is_active",sa.Boolean(),server_default=sa.text("true"),nullable=False),sa.Column("id",sa.Uuid(),primary_key=True),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()"),nullable=False),sa.UniqueConstraint("email",name="uq_users_email"))
 op.create_table("organization_users",sa.Column("organization_id",sa.Uuid(),nullable=False),sa.Column("user_id",sa.Uuid(),nullable=False),sa.Column("role",sa.Enum("owner","admin","member","viewer",name="organization_role"),server_default="member",nullable=False),sa.Column("id",sa.Uuid(),primary_key=True),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()"),nullable=False),sa.ForeignKeyConstraint(["organization_id"],["organizations.id"],ondelete="CASCADE"),sa.ForeignKeyConstraint(["user_id"],["users.id"],ondelete="CASCADE"),sa.UniqueConstraint("organization_id","user_id",name="uq_org_user_membership"))
 op.create_table("vehicles",sa.Column("organization_id",sa.Uuid(),nullable=False),sa.Column("registration_number",sa.String(40),nullable=False),sa.Column("make",sa.String(100)),sa.Column("model",sa.String(100)),sa.Column("id",sa.Uuid(),primary_key=True),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()"),nullable=False),sa.ForeignKeyConstraint(["organization_id"],["organizations.id"],ondelete="CASCADE"),sa.UniqueConstraint("organization_id","id",name="uq_vehicle_org_id"),sa.UniqueConstraint("organization_id","registration_number",name="uq_vehicle_org_registration"))
 op.create_index("ix_vehicles_organization_id","vehicles",["organization_id"])
 op.create_table("devices",sa.Column("organization_id",sa.Uuid(),nullable=False),sa.Column("identifier",sa.String(100),nullable=False),sa.Column("vehicle_id",sa.Uuid()),sa.Column("id",sa.Uuid(),primary_key=True),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.text("now()"),nullable=False),sa.ForeignKeyConstraint(["organization_id"],["organizations.id"],ondelete="CASCADE"),sa.ForeignKeyConstraint(["organization_id","vehicle_id"],["vehicles.organization_id","vehicles.id"],name="fk_device_vehicle_same_org",ondelete="CASCADE"),sa.UniqueConstraint("organization_id","id",name="uq_device_org_id"),sa.UniqueConstraint("organization_id","identifier",name="uq_device_org_identifier"))
 op.create_index("ix_devices_organization_id","devices",["organization_id"])
def downgrade():
 op.drop_index("ix_devices_organization_id",table_name="devices"); op.drop_table("devices")
 op.drop_index("ix_vehicles_organization_id",table_name="vehicles"); op.drop_table("vehicles")
 op.drop_table("organization_users"); op.drop_table("users"); op.drop_table("organizations")
