"""Add password credentials, role names, and revocable refresh sessions."""
from alembic import op
import sqlalchemy as sa
revision = "0003_authentication"
down_revision = "0002_device_vehicle_org_fk"
branch_labels = None
depends_on = None
def upgrade() -> None:
    op.add_column("users", sa.Column("hashed_password", sa.String(length=255), nullable=True))
    op.execute("ALTER TYPE organization_role RENAME VALUE 'member' TO 'manager'")
    op.create_table(
        "auth_refresh_sessions",
        sa.Column("jti", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("jti"),
    )
    op.create_index("ix_auth_refresh_sessions_user_id", "auth_refresh_sessions", ["user_id"])
    op.create_index("ix_auth_refresh_sessions_organization_id", "auth_refresh_sessions", ["organization_id"])
def downgrade() -> None:
    op.drop_index("ix_auth_refresh_sessions_organization_id", table_name="auth_refresh_sessions")
    op.drop_index("ix_auth_refresh_sessions_user_id", table_name="auth_refresh_sessions")
    op.drop_table("auth_refresh_sessions")
    op.execute("ALTER TYPE organization_role RENAME VALUE 'manager' TO 'member'")
    op.drop_column("users", "hashed_password")
