"""Add profile, repository, and task fields.

Revision ID: a7d2c18e4f60
Revises: 0088a4c32bfc
Create Date: 2026-10-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a7d2c18e4f60'
down_revision: Union[str, Sequence[str], None] = '0088a4c32bfc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.add_column(
        'users',
        sa.Column('tech_stack', sa.JSON(), nullable=False, server_default=sa.text("'[]'"))
    )

    op.add_column('projects', sa.Column('repository_url', sa.String(), nullable=True))
    op.add_column('tasks', sa.Column('commit_url', sa.String(), nullable=True))

    op.execute(
        """
        UPDATE tasks
        SET status = CASE
            WHEN status IN ('open', 'todo', 'not started', 'not-started') THEN 'not_started'
            WHEN status IN ('in progress', 'in-progress') THEN 'in_progress'
            WHEN status IN ('waiting_review', 'waiting review', 'in_review') THEN 'review'
            WHEN status IN ('done', 'complete') THEN 'completed'
            WHEN status IN ('not_started', 'in_progress', 'review', 'completed') THEN status
            ELSE 'not_started'
        END
        """
    )
    op.alter_column('tasks', 'status', server_default='not_started')
    op.create_check_constraint(
        'ck_tasks_status',
        'tasks',
        "status IN ('not_started', 'in_progress', 'review', 'completed')"
    )


def downgrade() -> None:
    op.drop_constraint('ck_tasks_status', 'tasks', type_='check')
    op.alter_column('tasks', 'status', server_default='open')
    op.drop_column('tasks', 'commit_url')
    op.drop_column('projects', 'repository_url')
    op.drop_column('users', 'tech_stack')
    op.drop_constraint('uq_users_email', 'users', type_='unique')
    op.drop_column('users', 'email')
