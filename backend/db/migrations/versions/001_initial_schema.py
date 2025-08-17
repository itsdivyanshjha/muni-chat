"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-01-16 13:43:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create dim_geo table
    op.create_table('dim_geo',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('state', sa.Text(), nullable=True),
        sa.Column('district', sa.Text(), nullable=True),
        sa.Column('zone', sa.Text(), nullable=True),
        sa.Column('ward', sa.Text(), nullable=True),
        sa.Column('level', sa.Text(), nullable=False),
        sa.CheckConstraint("level IN ('state', 'district', 'zone', 'ward')", name='check_geo_level'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create dim_time table
    op.create_table('dim_time',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('quarter', sa.Integer(), nullable=True),
        sa.Column('month', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create dim_indicator table
    op.create_table('dim_indicator',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('slug', sa.Text(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('unit', sa.Text(), nullable=False),
        sa.Column('category', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('default_agg', sa.Text(), nullable=False),
        sa.CheckConstraint("default_agg IN ('SUM', 'AVG', 'MAX', 'MIN')", name='check_default_agg'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    
    # Create fact_measure table
    op.create_table('fact_measure',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('indicator_id', sa.Integer(), nullable=False),
        sa.Column('geo_id', sa.Integer(), nullable=False),
        sa.Column('time_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Numeric(), nullable=True),
        sa.Column('quality_flag', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['geo_id'], ['dim_geo.id'], ),
        sa.ForeignKeyConstraint(['indicator_id'], ['dim_indicator.id'], ),
        sa.ForeignKeyConstraint(['time_id'], ['dim_time.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('indicator_id', 'geo_id', 'time_id')
    )
    
    # Create indexes
    op.create_index('idx_fact_keys', 'fact_measure', ['indicator_id', 'geo_id', 'time_id'])
    op.create_index('idx_time_year_quarter_month', 'dim_time', ['year', 'quarter', 'month'])


def downgrade() -> None:
    op.drop_index('idx_time_year_quarter_month', table_name='dim_time')
    op.drop_index('idx_fact_keys', table_name='fact_measure')
    op.drop_table('fact_measure')
    op.drop_table('dim_indicator')
    op.drop_table('dim_time')
    op.drop_table('dim_geo')
