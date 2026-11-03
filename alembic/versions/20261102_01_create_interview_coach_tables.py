"""create interview coach tables

Revision ID: 20261102_01
Revises:
Create Date: 2026-11-02 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20261102_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "interview_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("job_title", sa.String(length=300), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=True),
        sa.Column("user_segment", sa.String(length=50), nullable=False),
        sa.Column("mode", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_interview_sessions_user_id", "interview_sessions", ["user_id"])
    op.create_index("ix_interview_sessions_job_id", "interview_sessions", ["job_id"])
    op.create_index("ix_interview_sessions_status", "interview_sessions", ["status"])

    op.create_table(
        "transcript_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("speaker", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("session_id", "sequence", name="uq_transcript_message_sequence"),
    )
    op.create_index("ix_transcript_messages_session_id", "transcript_messages", ["session_id"])

    op.create_table(
        "interview_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("technical_score", sa.Integer(), nullable=False),
        sa.Column("behavioral_score", sa.Integer(), nullable=False),
        sa.Column("communication_score", sa.Integer(), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("strengths", sa.JSON(), nullable=False),
        sa.Column("improvement_areas", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_interview_reports_session_id", "interview_reports", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_interview_reports_session_id", table_name="interview_reports")
    op.drop_table("interview_reports")
    op.drop_index("ix_transcript_messages_session_id", table_name="transcript_messages")
    op.drop_table("transcript_messages")
    op.drop_index("ix_interview_sessions_status", table_name="interview_sessions")
    op.drop_index("ix_interview_sessions_job_id", table_name="interview_sessions")
    op.drop_index("ix_interview_sessions_user_id", table_name="interview_sessions")
    op.drop_table("interview_sessions")
