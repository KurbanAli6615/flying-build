"""2026-01-17-17_36

Revision ID: ab53ff3f91ae
Revises: f713818a02ec
Create Date: 2026-01-17 17:36:48.827927

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "ab53ff3f91ae"
down_revision = "f713818a02ec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the enum type first
    op.execute("CREATE TYPE teamstatus AS ENUM ('ACTIVE', 'DELETED')")

    # Add the status column with the enum type
    op.add_column(
        "teams",
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "DELETED", name="teamstatus", create_type=False),
            nullable=False,
            server_default="ACTIVE",
        ),
    )
    op.create_index(op.f("ix_teams_status"), "teams", ["status"], unique=False)


def downgrade() -> None:
    # Drop index and column first
    op.drop_index(op.f("ix_teams_status"), table_name="teams")
    op.drop_column("teams", "status")

    # Drop the enum type
    op.execute("DROP TYPE teamstatus")
