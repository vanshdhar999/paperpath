"""Initial schema

Revision ID: 001
Create Date: 2026-07-14
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable pgvector (must be done in Supabase SQL editor first, but safe to re-run)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("name", sa.String),
        sa.Column("username", sa.String, unique=True),
        sa.Column("domain_interests", sa.ARRAY(sa.String), default=list),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "papers",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("arxiv_id", sa.String, unique=True, nullable=False),
        sa.Column("semantic_scholar_id", sa.String),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("authors", sa.ARRAY(sa.String)),
        sa.Column("abstract", sa.Text),
        sa.Column("pdf_url", sa.String),
        sa.Column("published_date", sa.Date),
        sa.Column("venue", sa.String),
        sa.Column("full_text", sa.Text),
        sa.Column("journey_cache", sa.JSON),
        sa.Column("quiz_cache", sa.JSON),
        sa.Column("embedding", Vector(384)),
        sa.Column("difficulty_tier", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "prerequisites",
        sa.Column("paper_id", UUID(as_uuid=False), sa.ForeignKey("papers.id"), primary_key=True),
        sa.Column("prerequisite_paper_id", UUID(as_uuid=False), sa.ForeignKey("papers.id"), primary_key=True),
    )

    op.create_table(
        "tracks",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("domain", sa.String, nullable=False),
        sa.Column("name", sa.String, nullable=False),
    )

    op.create_table(
        "track_papers",
        sa.Column("track_id", UUID(as_uuid=False), sa.ForeignKey("tracks.id"), primary_key=True),
        sa.Column("paper_id", UUID(as_uuid=False), sa.ForeignKey("papers.id"), primary_key=True),
        sa.Column("order_hint", sa.Integer, default=0),
    )

    op.create_table(
        "user_progress",
        sa.Column("user_id", UUID(as_uuid=False), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("paper_id", UUID(as_uuid=False), sa.ForeignKey("papers.id"), primary_key=True),
        sa.Column("status", sa.String, default="locked"),
        sa.Column("quiz_score", sa.Integer),
        sa.Column("completed_at", sa.DateTime),
    )

    op.create_table(
        "quizzes",
        sa.Column("id", UUID(as_uuid=False), primary_key=True),
        sa.Column("paper_id", UUID(as_uuid=False), sa.ForeignKey("papers.id"), unique=True, nullable=False),
        sa.Column("questions", sa.JSON, nullable=False),
        sa.Column("generated_at", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("quizzes")
    op.drop_table("user_progress")
    op.drop_table("track_papers")
    op.drop_table("tracks")
    op.drop_table("prerequisites")
    op.drop_table("papers")
    op.drop_table("users")
