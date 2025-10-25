"""Add backtest_runs and backtest_daily_results tables for persistent backtest storage

Revision ID: 5a8c9d0e1f4g
Revises: 4a7b8c9d0e3f
Create Date: 2025-10-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5a8c9d0e1f4g'
down_revision = '4a7b8c9d0e3f'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create backtest_runs table
    if 'backtest_runs' not in existing_tables:
        op.create_table(
            'backtest_runs',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),

            # Run metadata
            sa.Column('name', sa.String(200), nullable=True),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('status', sa.String(50), nullable=False, server_default='IDLE', index=True),

            # Backtest parameters
            sa.Column('tickers', sa.JSON, nullable=False),
            sa.Column('start_date', sa.Date, nullable=False, index=True),
            sa.Column('end_date', sa.Date, nullable=False, index=True),
            sa.Column('initial_capital', sa.Float, nullable=False),

            # Performance metrics (summary)
            sa.Column('final_portfolio_value', sa.Float, nullable=True),
            sa.Column('total_return_pct', sa.Float, nullable=True),
            sa.Column('sharpe_ratio', sa.Float, nullable=True),
            sa.Column('sortino_ratio', sa.Float, nullable=True),
            sa.Column('max_drawdown', sa.Float, nullable=True),
            sa.Column('max_drawdown_date', sa.Date, nullable=True),
            sa.Column('long_short_ratio', sa.Float, nullable=True),
            sa.Column('gross_exposure', sa.Float, nullable=True),
            sa.Column('net_exposure', sa.Float, nullable=True),

            # Configuration (stored as JSON)
            sa.Column('graph_config', sa.JSON, nullable=True),
            sa.Column('agent_models', sa.JSON, nullable=True),
            sa.Column('request_data', sa.JSON, nullable=True),
            sa.Column('final_portfolio', sa.JSON, nullable=True),

            # Error tracking
            sa.Column('error_message', sa.Text, nullable=True),
        )

        # Create indexes for backtest_runs
        op.create_index('idx_status_created', 'backtest_runs', ['status', 'created_at'])
        op.create_index('idx_date_range', 'backtest_runs', ['start_date', 'end_date'])

    # Create backtest_daily_results table
    if 'backtest_daily_results' not in existing_tables:
        op.create_table(
            'backtest_daily_results',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('backtest_run_id', sa.Integer, sa.ForeignKey('backtest_runs.id', ondelete='CASCADE'), nullable=False, index=True),
            sa.Column('date', sa.Date, nullable=False, index=True),

            # Portfolio state
            sa.Column('portfolio_value', sa.Float, nullable=False),
            sa.Column('cash', sa.Float, nullable=False),

            # Trading activity (stored as JSON)
            sa.Column('decisions', sa.JSON, nullable=True),
            sa.Column('executed_trades', sa.JSON, nullable=True),
            sa.Column('analyst_signals', sa.JSON, nullable=True),
            sa.Column('current_prices', sa.JSON, nullable=True),

            # Exposure metrics
            sa.Column('long_exposure', sa.Float, nullable=True),
            sa.Column('short_exposure', sa.Float, nullable=True),
            sa.Column('gross_exposure', sa.Float, nullable=True),
            sa.Column('net_exposure', sa.Float, nullable=True),
            sa.Column('long_short_ratio', sa.Float, nullable=True),

            # Performance metrics
            sa.Column('portfolio_return_pct', sa.Float, nullable=True),

            # Metadata
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

        # Create composite index for backtest_daily_results
        op.create_index('idx_backtest_date', 'backtest_daily_results', ['backtest_run_id', 'date'], unique=True)


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Drop backtest_daily_results table
    if 'backtest_daily_results' in existing_tables:
        try:
            op.drop_index('idx_backtest_date', 'backtest_daily_results')
        except:
            pass
        op.drop_table('backtest_daily_results')

    # Drop backtest_runs table
    if 'backtest_runs' in existing_tables:
        try:
            op.drop_index('idx_date_range', 'backtest_runs')
            op.drop_index('idx_status_created', 'backtest_runs')
        except:
            pass
        op.drop_table('backtest_runs')
