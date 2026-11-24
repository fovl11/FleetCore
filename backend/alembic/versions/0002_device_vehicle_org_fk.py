"""Enforce that a device and its vehicle belong to the same organization."""
from alembic import op

revision = "0002_device_vehicle_org_fk"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 0001 contains these constraints in newer checkouts, but databases that
    # already applied an earlier 0001 may not have them. Normalize safely.
    op.execute("""
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'vehicles'::regclass AND conname = 'uq_vehicle_org_id'
      ) THEN
        ALTER TABLE vehicles ADD CONSTRAINT uq_vehicle_org_id UNIQUE (organization_id, id);
      END IF;
      IF EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid = 'devices'::regclass AND conname = 'fk_device_vehicle_same_org'
      ) THEN
        ALTER TABLE devices DROP CONSTRAINT fk_device_vehicle_same_org;
      END IF;
      ALTER TABLE devices ADD CONSTRAINT fk_device_vehicle_same_org
        FOREIGN KEY (organization_id, vehicle_id)
        REFERENCES vehicles (organization_id, id) ON DELETE CASCADE;
    END $$;
    """)

def downgrade() -> None:
    op.drop_constraint("fk_device_vehicle_same_org", "devices", type_="foreignkey")
