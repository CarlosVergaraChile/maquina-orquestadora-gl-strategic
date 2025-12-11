"""Initial schema migration for Máquina Orquestadora.

Revision ID: 001
Revises: None
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create initial schema."""
    op.create_table(
        'orchestration_contexts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
    )

    op.create_table(
        'decisions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('context_id', sa.String(36), sa.ForeignKey('orchestration_contexts.id')),
        sa.Column('decision_type', sa.String(50), nullable=False),
        sa.Column('metadata', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )

    op.create_table(
        'model_responses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('decision_id', sa.String(36), sa.ForeignKey('decisions.id')),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('response_text', sa.Text, nullable=False),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )

    op.create_table(
        'human_feedback',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('decision_id', sa.String(36), sa.ForeignKey('decisions.id')),
        sa.Column('feedback_text', sa.Text, nullable=False),
        sa.Column('rating', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )

def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('human_feedback')
    op.drop_table('model_responses')
    op.drop_table('decisions')
    op.drop_table('orchestration_contexts')
