"""Add missing campaign columns and relationships

Revision ID: add_missing_columns_001
Revises: 
Create Date: 2025-01-04

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers
revision = 'add_missing_columns_001'
down_revision = None
branch_labels = None
depends_on = None


def column_exists(table_name, column_name, schema='campaigns'):
    """Check if a column exists in a table"""
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns(table_name, schema=schema)]
    return column_name in columns


def upgrade():
    # Add missing columns to campaigns table only if they don't exist
    if not column_exists('campaigns', 'type'):
        op.add_column('campaigns', sa.Column('type', sa.String(50), nullable=True, default='performance'), schema='campaigns')
    
    if not column_exists('campaigns', 'budget'):
        op.add_column('campaigns', sa.Column('budget', sa.Numeric(12, 2), nullable=True), schema='campaigns')
    
    if not column_exists('campaigns', 'current_gmv'):
        op.add_column('campaigns', sa.Column('current_gmv', sa.Numeric(12, 2), nullable=True, default=0.00), schema='campaigns')
    
    if not column_exists('campaigns', 'current_posts'):
        op.add_column('campaigns', sa.Column('current_posts', sa.Integer(), nullable=True, default=0), schema='campaigns')
    
    if not column_exists('campaigns', 'current_creators'):
        op.add_column('campaigns', sa.Column('current_creators', sa.Integer(), nullable=True, default=0), schema='campaigns')
    
    if not column_exists('campaigns', 'target_creators'):
        op.add_column('campaigns', sa.Column('target_creators', sa.Integer(), nullable=True), schema='campaigns')
    
    if not column_exists('campaigns', 'total_views'):
        op.add_column('campaigns', sa.Column('total_views', sa.Integer(), nullable=True, default=0), schema='campaigns')
    
    if not column_exists('campaigns', 'total_engagement'):
        op.add_column('campaigns', sa.Column('total_engagement', sa.Integer(), nullable=True, default=0), schema='campaigns')
    
    # Add missing columns to deliverables table
    if not column_exists('deliverables', 'campaign_id'):
        op.add_column('deliverables', sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=True), schema='campaigns')
    
    if not column_exists('deliverables', 'creator_id'):
        op.add_column('deliverables', sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=True), schema='campaigns')
    
    if not column_exists('deliverables', 'title'):
        op.add_column('deliverables', sa.Column('title', sa.String(255), nullable=True), schema='campaigns')
    
    if not column_exists('deliverables', 'description'):
        op.add_column('deliverables', sa.Column('description', sa.Text(), nullable=True), schema='campaigns')
    
    if not column_exists('deliverables', 'content_url'):
        op.add_column('deliverables', sa.Column('content_url', sa.Text(), nullable=True), schema='campaigns')
    
    if not column_exists('deliverables', 'content_type'):
        op.add_column('deliverables', sa.Column('content_type', sa.String(50), nullable=True), schema='campaigns')
    
    if not column_exists('deliverables', 'published_at'):
        op.add_column('deliverables', sa.Column('published_at', sa.DateTime(), nullable=True), schema='campaigns')
    
    if not column_exists('deliverables', 'feedback'):
        op.add_column('deliverables', sa.Column('feedback', sa.Text(), nullable=True), schema='campaigns')
    
    # Check if foreign key constraints exist before adding
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_fks = [fk['name'] for fk in inspector.get_foreign_keys('deliverables', schema='campaigns')]
    
    if 'fk_deliverables_campaign_id' not in existing_fks and column_exists('deliverables', 'campaign_id'):
        op.create_foreign_key(
            'fk_deliverables_campaign_id', 
            'deliverables', 
            'campaigns',
            ['campaign_id'], 
            ['id'],
            source_schema='campaigns',
            referent_schema='campaigns'
        )
    
    if 'fk_deliverables_creator_id' not in existing_fks and column_exists('deliverables', 'creator_id'):
        op.create_foreign_key(
            'fk_deliverables_creator_id',
            'deliverables',
            'users',
            ['creator_id'],
            ['id'],
            source_schema='campaigns',
            referent_schema='users'
        )
    
    # Update existing records with default values
    op.execute("UPDATE campaigns.campaigns SET type = 'performance' WHERE type IS NULL")
    op.execute("UPDATE campaigns.campaigns SET current_gmv = 0.00 WHERE current_gmv IS NULL")
    op.execute("UPDATE campaigns.campaigns SET current_posts = 0 WHERE current_posts IS NULL")
    op.execute("UPDATE campaigns.campaigns SET current_creators = 0 WHERE current_creators IS NULL")
    op.execute("UPDATE campaigns.campaigns SET total_views = 0 WHERE total_views IS NULL")
    op.execute("UPDATE campaigns.campaigns SET total_engagement = 0 WHERE total_engagement IS NULL")
    
    # Copy budget to total_budget where needed
    op.execute("UPDATE campaigns.campaigns SET budget = total_budget WHERE budget IS NULL AND total_budget IS NOT NULL")
    op.execute("UPDATE campaigns.campaigns SET total_budget = budget WHERE total_budget IS NULL AND budget IS NOT NULL")
    
    # Update deliverables with campaign_id and creator_id from applications
    op.execute("""
        UPDATE campaigns.deliverables d
        SET campaign_id = ca.campaign_id,
            creator_id = ca.creator_id
        FROM campaigns.creator_applications ca
        WHERE d.application_id = ca.id
        AND (d.campaign_id IS NULL OR d.creator_id IS NULL)
    """)
    
    # Only set NOT NULL if column exists and has no nulls
    if column_exists('campaigns', 'type'):
        op.execute("UPDATE campaigns.campaigns SET type = 'performance' WHERE type IS NULL")
        op.alter_column('campaigns', 'type', nullable=False, schema='campaigns')


def downgrade():
    # Drop foreign key constraints if they exist
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_fks = [fk['name'] for fk in inspector.get_foreign_keys('deliverables', schema='campaigns')]
    
    if 'fk_deliverables_campaign_id' in existing_fks:
        op.drop_constraint('fk_deliverables_campaign_id', 'deliverables', schema='campaigns', type_='foreignkey')
    
    if 'fk_deliverables_creator_id' in existing_fks:
        op.drop_constraint('fk_deliverables_creator_id', 'deliverables', schema='campaigns', type_='foreignkey')
    
    # Drop columns from deliverables if they exist
    if column_exists('deliverables', 'feedback'):
        op.drop_column('deliverables', 'feedback', schema='campaigns')
    if column_exists('deliverables', 'published_at'):
        op.drop_column('deliverables', 'published_at', schema='campaigns')
    if column_exists('deliverables', 'content_type'):
        op.drop_column('deliverables', 'content_type', schema='campaigns')
    if column_exists('deliverables', 'content_url'):
        op.drop_column('deliverables', 'content_url', schema='campaigns')
    if column_exists('deliverables', 'description'):
        op.drop_column('deliverables', 'description', schema='campaigns')
    if column_exists('deliverables', 'title'):
        op.drop_column('deliverables', 'title', schema='campaigns')
    if column_exists('deliverables', 'creator_id'):
        op.drop_column('deliverables', 'creator_id', schema='campaigns')
    if column_exists('deliverables', 'campaign_id'):
        op.drop_column('deliverables', 'campaign_id', schema='campaigns')
    
    # Drop columns from campaigns if they exist
    if column_exists('campaigns', 'total_engagement'):
        op.drop_column('campaigns', 'total_engagement', schema='campaigns')
    if column_exists('campaigns', 'total_views'):
        op.drop_column('campaigns', 'total_views', schema='campaigns')
    if column_exists('campaigns', 'target_creators'):
        op.drop_column('campaigns', 'target_creators', schema='campaigns')
    if column_exists('campaigns', 'current_creators'):
        op.drop_column('campaigns', 'current_creators', schema='campaigns')
    if column_exists('campaigns', 'current_posts'):
        op.drop_column('campaigns', 'current_posts', schema='campaigns')
    if column_exists('campaigns', 'current_gmv'):
        op.drop_column('campaigns', 'current_gmv', schema='campaigns')
    if column_exists('campaigns', 'budget'):
        op.drop_column('campaigns', 'budget', schema='campaigns')
    if column_exists('campaigns', 'type'):
        op.drop_column('campaigns', 'type', schema='campaigns')