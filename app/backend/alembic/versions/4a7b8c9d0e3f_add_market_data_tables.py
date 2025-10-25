"""Add market data tables for caching historical prices, financial metrics, news, and insider trades

Revision ID: 4a7b8c9d0e3f
Revises: 3f9a6b7c8d2e
Create Date: 2025-10-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4a7b8c9d0e3f'
down_revision = '3f9a6b7c8d2e'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create historical_prices table
    if 'historical_prices' not in existing_tables:
        op.create_table(
            'historical_prices',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('ticker', sa.String(20), nullable=False, index=True),
            sa.Column('date', sa.Date, nullable=False, index=True),
            sa.Column('open', sa.Float, nullable=False),
            sa.Column('high', sa.Float, nullable=False),
            sa.Column('low', sa.Float, nullable=False),
            sa.Column('close', sa.Float, nullable=False),
            sa.Column('volume', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('data_source', sa.String(50), nullable=False),
        )
        op.create_index('idx_ticker_date', 'historical_prices', ['ticker', 'date'], unique=True)

    # Create financial_metrics table
    if 'financial_metrics' not in existing_tables:
        op.create_table(
            'financial_metrics',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('ticker', sa.String(20), nullable=False, index=True),
            sa.Column('report_period', sa.Date, nullable=False, index=True),
            sa.Column('period', sa.String(20), nullable=False),
            sa.Column('currency', sa.String(10), nullable=False),
            # Valuation metrics
            sa.Column('market_cap', sa.Float, nullable=True),
            sa.Column('enterprise_value', sa.Float, nullable=True),
            sa.Column('price_to_earnings_ratio', sa.Float, nullable=True),
            sa.Column('price_to_book_ratio', sa.Float, nullable=True),
            sa.Column('price_to_sales_ratio', sa.Float, nullable=True),
            sa.Column('enterprise_value_to_ebitda_ratio', sa.Float, nullable=True),
            sa.Column('enterprise_value_to_revenue_ratio', sa.Float, nullable=True),
            sa.Column('free_cash_flow_yield', sa.Float, nullable=True),
            sa.Column('peg_ratio', sa.Float, nullable=True),
            # Profitability metrics
            sa.Column('gross_margin', sa.Float, nullable=True),
            sa.Column('operating_margin', sa.Float, nullable=True),
            sa.Column('net_margin', sa.Float, nullable=True),
            sa.Column('return_on_equity', sa.Float, nullable=True),
            sa.Column('return_on_assets', sa.Float, nullable=True),
            sa.Column('return_on_invested_capital', sa.Float, nullable=True),
            # Efficiency metrics
            sa.Column('asset_turnover', sa.Float, nullable=True),
            sa.Column('inventory_turnover', sa.Float, nullable=True),
            sa.Column('receivables_turnover', sa.Float, nullable=True),
            sa.Column('days_sales_outstanding', sa.Float, nullable=True),
            sa.Column('operating_cycle', sa.Float, nullable=True),
            sa.Column('working_capital_turnover', sa.Float, nullable=True),
            # Liquidity metrics
            sa.Column('current_ratio', sa.Float, nullable=True),
            sa.Column('quick_ratio', sa.Float, nullable=True),
            sa.Column('cash_ratio', sa.Float, nullable=True),
            sa.Column('operating_cash_flow_ratio', sa.Float, nullable=True),
            # Leverage metrics
            sa.Column('debt_to_equity', sa.Float, nullable=True),
            sa.Column('debt_to_assets', sa.Float, nullable=True),
            sa.Column('interest_coverage', sa.Float, nullable=True),
            # Growth metrics
            sa.Column('revenue_growth', sa.Float, nullable=True),
            sa.Column('earnings_growth', sa.Float, nullable=True),
            sa.Column('book_value_growth', sa.Float, nullable=True),
            sa.Column('earnings_per_share_growth', sa.Float, nullable=True),
            sa.Column('free_cash_flow_growth', sa.Float, nullable=True),
            sa.Column('operating_income_growth', sa.Float, nullable=True),
            sa.Column('ebitda_growth', sa.Float, nullable=True),
            # Per-share metrics
            sa.Column('payout_ratio', sa.Float, nullable=True),
            sa.Column('earnings_per_share', sa.Float, nullable=True),
            sa.Column('book_value_per_share', sa.Float, nullable=True),
            sa.Column('free_cash_flow_per_share', sa.Float, nullable=True),
            # Metadata
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('data_source', sa.String(50), nullable=False),
        )
        op.create_index('idx_ticker_report_period', 'financial_metrics', ['ticker', 'report_period', 'period'], unique=True)

    # Create company_news table
    if 'company_news' not in existing_tables:
        op.create_table(
            'company_news',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('ticker', sa.String(20), nullable=False, index=True),
            sa.Column('title', sa.Text, nullable=False),
            sa.Column('author', sa.String(200), nullable=True),
            sa.Column('source', sa.String(200), nullable=False),
            sa.Column('date', sa.Date, nullable=False, index=True),
            sa.Column('url', sa.Text, nullable=False),
            sa.Column('sentiment', sa.String(20), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('data_source', sa.String(50), nullable=False),
        )
        op.create_index('idx_ticker_date_news', 'company_news', ['ticker', 'date'])
        op.create_index('idx_url_unique', 'company_news', ['url'], unique=True)

    # Create insider_trades table
    if 'insider_trades' not in existing_tables:
        op.create_table(
            'insider_trades',
            sa.Column('id', sa.Integer, primary_key=True, index=True),
            sa.Column('ticker', sa.String(20), nullable=False, index=True),
            sa.Column('issuer', sa.String(200), nullable=True),
            sa.Column('name', sa.String(200), nullable=True),
            sa.Column('title', sa.String(200), nullable=True),
            sa.Column('is_board_director', sa.Boolean, nullable=True),
            sa.Column('transaction_date', sa.Date, nullable=True, index=True),
            sa.Column('transaction_shares', sa.Float, nullable=True),
            sa.Column('transaction_price_per_share', sa.Float, nullable=True),
            sa.Column('transaction_value', sa.Float, nullable=True),
            sa.Column('shares_owned_before_transaction', sa.Float, nullable=True),
            sa.Column('shares_owned_after_transaction', sa.Float, nullable=True),
            sa.Column('security_title', sa.String(200), nullable=True),
            sa.Column('filing_date', sa.Date, nullable=False, index=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column('data_source', sa.String(50), nullable=False),
        )
        op.create_index('idx_ticker_filing_date', 'insider_trades', ['ticker', 'filing_date'])
        op.create_index('idx_ticker_transaction_date', 'insider_trades', ['ticker', 'transaction_date'])


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Drop insider_trades table
    if 'insider_trades' in existing_tables:
        try:
            op.drop_index('idx_ticker_transaction_date', 'insider_trades')
            op.drop_index('idx_ticker_filing_date', 'insider_trades')
        except:
            pass
        op.drop_table('insider_trades')

    # Drop company_news table
    if 'company_news' in existing_tables:
        try:
            op.drop_index('idx_url_unique', 'company_news')
            op.drop_index('idx_ticker_date_news', 'company_news')
        except:
            pass
        op.drop_table('company_news')

    # Drop financial_metrics table
    if 'financial_metrics' in existing_tables:
        try:
            op.drop_index('idx_ticker_report_period', 'financial_metrics')
        except:
            pass
        op.drop_table('financial_metrics')

    # Drop historical_prices table
    if 'historical_prices' in existing_tables:
        try:
            op.drop_index('idx_ticker_date', 'historical_prices')
        except:
            pass
        op.drop_table('historical_prices')
