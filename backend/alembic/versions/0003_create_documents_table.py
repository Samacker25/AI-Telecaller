"""create documents table

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-19
"""

import sqlalchemy as sa

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("hospital_id", sa.Uuid(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=10), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("uploaded_by", sa.Uuid(), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_documents")),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            name=op.f("fk_documents_hospital_id_hospitals"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by"],
            ["users.id"],
            name=op.f("fk_documents_uploaded_by_users"),
            ondelete="SET NULL",
        ),
    )
    op.create_index(op.f("ix_documents_hospital_id"), "documents", ["hospital_id"], unique=False)
    op.create_index(op.f("ix_documents_status"), "documents", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_documents_status"), table_name="documents")
    op.drop_index(op.f("ix_documents_hospital_id"), table_name="documents")
    op.drop_table("documents")
