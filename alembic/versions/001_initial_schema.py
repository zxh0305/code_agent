"""Initial database schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('github_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('access_token', sa.String(length=255), nullable=True),
        sa.Column('refresh_token', sa.String(length=255), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('role', sa.String(length=50), server_default='user', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('github_id'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_github_id'), 'users', ['github_id'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create repositories table
    op.create_table(
        'repositories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('github_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('html_url', sa.String(length=500), nullable=True),
        sa.Column('clone_url', sa.String(length=500), nullable=True),
        sa.Column('default_branch', sa.String(length=100), server_default='main', nullable=True),
        sa.Column('is_private', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('language', sa.String(length=100), nullable=True),
        sa.Column('topics', sa.JSON(), nullable=True),
        sa.Column('stars_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('forks_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('local_path', sa.String(length=500), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('github_id')
    )
    op.create_index(op.f('ix_repositories_full_name'), 'repositories', ['full_name'], unique=True)
    op.create_index(op.f('ix_repositories_github_id'), 'repositories', ['github_id'], unique=True)
    op.create_index(op.f('ix_repositories_id'), 'repositories', ['id'], unique=False)

    # Create code_analyses table
    op.create_table(
        'code_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('repository_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=1000), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=True),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='pending', nullable=False),
        sa.Column('classes', sa.JSON(), nullable=True),
        sa.Column('functions', sa.JSON(), nullable=True),
        sa.Column('imports', sa.JSON(), nullable=True),
        sa.Column('dependencies', sa.JSON(), nullable=True),
        sa.Column('metrics', sa.JSON(), nullable=True),
        sa.Column('issues', sa.JSON(), nullable=True),
        sa.Column('suggestions', sa.JSON(), nullable=True),
        sa.Column('raw_ast', sa.JSON(), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('lines_of_code', sa.Integer(), nullable=True),
        sa.Column('complexity_score', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_code_analyses_id'), 'code_analyses', ['id'], unique=False)
    op.create_index('ix_code_analyses_repo_path', 'code_analyses', ['repository_id', 'file_path'], unique=False)

    # Create pull_requests table
    op.create_table(
        'pull_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('github_id', sa.Integer(), nullable=True),
        sa.Column('repository_id', sa.Integer(), nullable=False),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('number', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_branch', sa.String(length=255), nullable=False),
        sa.Column('target_branch', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='draft', nullable=False),
        sa.Column('is_draft', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('html_url', sa.String(length=500), nullable=True),
        sa.Column('diff_url', sa.String(length=500), nullable=True),
        sa.Column('commits_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('additions', sa.Integer(), server_default='0', nullable=True),
        sa.Column('deletions', sa.Integer(), server_default='0', nullable=True),
        sa.Column('changed_files', sa.Integer(), server_default='0', nullable=True),
        sa.Column('labels', sa.JSON(), nullable=True),
        sa.Column('reviewers', sa.JSON(), nullable=True),
        sa.Column('merge_commit_sha', sa.String(length=64), nullable=True),
        sa.Column('merged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('merged_by', sa.String(length=100), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pull_requests_id'), 'pull_requests', ['id'], unique=False)
    op.create_index('ix_pull_requests_repo_number', 'pull_requests', ['repository_id', 'number'], unique=True)

    # Create pr_reviews table
    op.create_table(
        'pr_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pull_request_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('github_id', sa.Integer(), nullable=True),
        sa.Column('state', sa.String(length=50), server_default='pending', nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('ai_generated', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('ai_model', sa.String(length=100), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['pull_request_id'], ['pull_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pr_reviews_id'), 'pr_reviews', ['id'], unique=False)

    # Create pr_comments table
    op.create_table(
        'pr_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('pull_request_id', sa.Integer(), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('github_id', sa.Integer(), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('path', sa.String(length=500), nullable=True),
        sa.Column('position', sa.Integer(), nullable=True),
        sa.Column('line', sa.Integer(), nullable=True),
        sa.Column('side', sa.String(length=10), nullable=True),
        sa.Column('commit_id', sa.String(length=64), nullable=True),
        sa.Column('in_reply_to_id', sa.Integer(), nullable=True),
        sa.Column('ai_generated', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['pull_request_id'], ['pull_requests.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['review_id'], ['pr_reviews.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pr_comments_id'), 'pr_comments', ['id'], unique=False)

    # Create system_settings table
    op.create_table(
        'system_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('is_sensitive', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    op.create_index(op.f('ix_system_settings_id'), 'system_settings', ['id'], unique=False)
    op.create_index(op.f('ix_system_settings_key'), 'system_settings', ['key'], unique=True)


def downgrade() -> None:
    """Drop all tables."""
    op.drop_index(op.f('ix_system_settings_key'), table_name='system_settings')
    op.drop_index(op.f('ix_system_settings_id'), table_name='system_settings')
    op.drop_table('system_settings')

    op.drop_index(op.f('ix_pr_comments_id'), table_name='pr_comments')
    op.drop_table('pr_comments')

    op.drop_index(op.f('ix_pr_reviews_id'), table_name='pr_reviews')
    op.drop_table('pr_reviews')

    op.drop_index('ix_pull_requests_repo_number', table_name='pull_requests')
    op.drop_index(op.f('ix_pull_requests_id'), table_name='pull_requests')
    op.drop_table('pull_requests')

    op.drop_index('ix_code_analyses_repo_path', table_name='code_analyses')
    op.drop_index(op.f('ix_code_analyses_id'), table_name='code_analyses')
    op.drop_table('code_analyses')

    op.drop_index(op.f('ix_repositories_id'), table_name='repositories')
    op.drop_index(op.f('ix_repositories_github_id'), table_name='repositories')
    op.drop_index(op.f('ix_repositories_full_name'), table_name='repositories')
    op.drop_table('repositories')

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_github_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
