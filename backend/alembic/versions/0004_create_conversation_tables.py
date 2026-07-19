"""create conversations and messages tables

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-19
"""

import sqlalchemy as sa

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "conversations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("hospital_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("escalated", sa.Boolean(), nullable=False),
        sa.Column("message_count", sa.Integer(), nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_conversations")),
        sa.ForeignKeyConstraint(
            ["hospital_id"],
            ["hospitals.id"],
            name=op.f("fk_conversations_hospital_id_hospitals"),
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        op.f("ix_conversations_session_id"), "conversations", ["session_id"], unique=True
    )
    op.create_index(
        op.f("ix_conversations_hospital_id"), "conversations", ["hospital_id"], unique=False
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("sender", sa.String(length=10), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("escalation_reason", sa.String(length=30), nullable=True),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_messages")),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            name=op.f("fk_messages_conversation_id_conversations"),
            ondelete="CASCADE",
        ),
    )
    op.create_index(op.f("ix_messages_conversation_id"), "messages", ["conversation_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_messages_conversation_id"), table_name="messages")
    op.drop_table("messages")
    op.drop_index(op.f("ix_conversations_hospital_id"), table_name="conversations")
    op.drop_index(op.f("ix_conversations_session_id"), table_name="conversations")
    op.drop_table("conversations")
