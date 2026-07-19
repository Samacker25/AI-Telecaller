"""create hospitals, departments, and doctors tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-19
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "hospitals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("settings", JSON_TYPE, nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_hospitals")),
    )

    op.create_table(
        "departments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hospital_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_departments")),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            name=op.f("fk_departments_hospital_id_hospitals"),
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("hospital_id", "name", name="uq_departments_hospital_id_name"),
    )
    op.create_index(
        op.f("ix_departments_hospital_id"), "departments", ["hospital_id"], unique=False
    )

    op.create_table(
        "doctors",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hospital_id", sa.Uuid(), nullable=False),
        sa.Column("department_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("specialization", sa.String(length=255), nullable=False),
        sa.Column("qualification", sa.String(length=255), nullable=True),
        sa.Column("opd_schedule", JSON_TYPE, nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        *_timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_doctors")),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            name=op.f("fk_doctors_hospital_id_hospitals"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            name=op.f("fk_doctors_department_id_departments"),
            ondelete="RESTRICT",
        ),
    )
    op.create_index(op.f("ix_doctors_hospital_id"), "doctors", ["hospital_id"], unique=False)
    op.create_index(op.f("ix_doctors_department_id"), "doctors", ["department_id"], unique=False)
    op.create_index(op.f("ix_doctors_specialization"), "doctors", ["specialization"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_doctors_specialization"), table_name="doctors")
    op.drop_index(op.f("ix_doctors_department_id"), table_name="doctors")
    op.drop_index(op.f("ix_doctors_hospital_id"), table_name="doctors")
    op.drop_table("doctors")
    op.drop_index(op.f("ix_departments_hospital_id"), table_name="departments")
    op.drop_table("departments")
    op.drop_table("hospitals")
