"""Add extended schema for government datasets

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create dataset_registry table
    op.create_table('dataset_registry',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.Text(), nullable=False),
        sa.Column('slug', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.Text(), nullable=False),
        sa.Column('subcategory', sa.Text(), nullable=True),
        sa.Column('api_endpoint', sa.Text(), nullable=False),
        sa.Column('api_key_required', sa.Boolean(), nullable=True),
        sa.Column('supported_formats', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('geographic_level', sa.Text(), nullable=False),
        sa.Column('time_granularity', sa.Text(), nullable=False),
        sa.Column('update_frequency', sa.Text(), nullable=True),
        sa.Column('source_department', sa.Text(), nullable=True),
        sa.Column('last_updated', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('resource_id'),
        sa.UniqueConstraint('slug')
    )
    
    # Create dataset_indicator table
    op.create_table('dataset_indicator',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dataset_id', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.Text(), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=False),
        sa.Column('data_type', sa.Text(), nullable=False),
        sa.Column('unit', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_filterable', sa.Boolean(), nullable=True),
        sa.Column('is_measure', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['dataset_registry.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create data_source table
    op.create_table('data_source',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dataset_id', sa.Integer(), nullable=False),
        sa.Column('source_type', sa.Text(), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('last_sync', sa.Date(), nullable=True),
        sa.Column('sync_status', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('records_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['dataset_registry.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create geographic_hierarchy table
    op.create_table('geographic_hierarchy',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('geo_id', sa.Integer(), nullable=False),
        sa.Column('parent_geo_id', sa.Integer(), nullable=True),
        sa.Column('hierarchy_level', sa.Integer(), nullable=False),
        sa.Column('census_code', sa.Text(), nullable=True),
        sa.Column('official_name', sa.Text(), nullable=True),
        sa.Column('alternate_names', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['geo_id'], ['dim_geo.id'], ),
        sa.ForeignKeyConstraint(['parent_geo_id'], ['dim_geo.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create extended_fact_measure table
    op.create_table('extended_fact_measure',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dataset_id', sa.Integer(), nullable=False),
        sa.Column('indicator_id', sa.Integer(), nullable=False),
        sa.Column('geo_id', sa.Integer(), nullable=False),
        sa.Column('time_id', sa.Integer(), nullable=False),
        sa.Column('numeric_value', sa.Numeric(), nullable=True),
        sa.Column('string_value', sa.Text(), nullable=True),
        sa.Column('boolean_value', sa.Boolean(), nullable=True),
        sa.Column('date_value', sa.Date(), nullable=True),
        sa.Column('source_record_id', sa.Text(), nullable=True),
        sa.Column('quality_flag', sa.Text(), nullable=True),
        sa.Column('ingestion_timestamp', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['dataset_registry.id'], ),
        sa.ForeignKeyConstraint(['indicator_id'], ['dataset_indicator.id'], ),
        sa.ForeignKeyConstraint(['geo_id'], ['dim_geo.id'], ),
        sa.ForeignKeyConstraint(['time_id'], ['dim_time.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create data_quality_log table
    op.create_table('data_quality_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dataset_id', sa.Integer(), nullable=False),
        sa.Column('sync_timestamp', sa.Date(), nullable=True),
        sa.Column('records_processed', sa.Integer(), nullable=False),
        sa.Column('records_valid', sa.Integer(), nullable=False),
        sa.Column('records_invalid', sa.Integer(), nullable=False),
        sa.Column('validation_errors', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('quality_score', sa.Numeric(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['dataset_id'], ['dataset_registry.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for performance
    op.create_index('idx_extended_fact_dataset', 'extended_fact_measure', ['dataset_id'])
    op.create_index('idx_extended_fact_indicator', 'extended_fact_measure', ['indicator_id'])
    op.create_index('idx_extended_fact_geo', 'extended_fact_measure', ['geo_id'])
    op.create_index('idx_extended_fact_time', 'extended_fact_measure', ['time_id'])
    op.create_index('idx_geo_hierarchy_level', 'geographic_hierarchy', ['hierarchy_level'])
    op.create_index('idx_dataset_category', 'dataset_registry', ['category'])
    op.create_index('idx_dataset_geo_level', 'dataset_registry', ['geographic_level'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_dataset_geo_level', table_name='dataset_registry')
    op.drop_index('idx_dataset_category', table_name='dataset_registry')
    op.drop_index('idx_geo_hierarchy_level', table_name='geographic_hierarchy')
    op.drop_index('idx_extended_fact_time', table_name='extended_fact_measure')
    op.drop_index('idx_extended_fact_geo', table_name='extended_fact_measure')
    op.drop_index('idx_extended_fact_indicator', table_name='extended_fact_measure')
    op.drop_index('idx_extended_fact_dataset', table_name='extended_fact_measure')
    
    # Drop tables
    op.drop_table('data_quality_log')
    op.drop_table('extended_fact_measure')
    op.drop_table('geographic_hierarchy')
    op.drop_table('data_source')
    op.drop_table('dataset_indicator')
    op.drop_table('dataset_registry')
