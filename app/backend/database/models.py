from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey, Float, Date, Index
from sqlalchemy.sql import func
from .connection import Base


class HedgeFundFlow(Base):
    """Table to store React Flow configurations (nodes, edges, viewport)"""
    __tablename__ = "hedge_fund_flows"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Flow metadata
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # React Flow state
    nodes = Column(JSON, nullable=False)  # Store React Flow nodes as JSON
    edges = Column(JSON, nullable=False)  # Store React Flow edges as JSON
    viewport = Column(JSON, nullable=True)  # Store viewport state (zoom, x, y)
    data = Column(JSON, nullable=True)  # Store node internal states (tickers, models, etc.)
    
    # Additional metadata
    is_template = Column(Boolean, default=False)  # Mark as template for reuse
    tags = Column(JSON, nullable=True)  # Store tags for categorization


class HedgeFundFlowRun(Base):
    """Table to track individual execution runs of a hedge fund flow"""
    __tablename__ = "hedge_fund_flow_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("hedge_fund_flows.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Run execution tracking
    status = Column(String(50), nullable=False, default="IDLE")  # IDLE, IN_PROGRESS, COMPLETE, ERROR
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Run configuration
    trading_mode = Column(String(50), nullable=False, default="one-time")  # one-time, continuous, advisory
    schedule = Column(String(50), nullable=True)  # hourly, daily, weekly (for continuous mode)
    duration = Column(String(50), nullable=True)  # 1day, 1week, 1month (for continuous mode)
    
    # Run data
    request_data = Column(JSON, nullable=True)  # Store the request parameters (tickers, agents, models, etc.)
    initial_portfolio = Column(JSON, nullable=True)  # Store initial portfolio state
    final_portfolio = Column(JSON, nullable=True)  # Store final portfolio state
    results = Column(JSON, nullable=True)  # Store the output/results from the run
    error_message = Column(Text, nullable=True)  # Store error details if run failed
    
    # Metadata
    run_number = Column(Integer, nullable=False, default=1)  # Sequential run number for this flow


class HedgeFundFlowRunCycle(Base):
    """Individual analysis cycles within a trading session"""
    __tablename__ = "hedge_fund_flow_run_cycles"
    
    id = Column(Integer, primary_key=True, index=True)
    flow_run_id = Column(Integer, ForeignKey("hedge_fund_flow_runs.id"), nullable=False, index=True)
    cycle_number = Column(Integer, nullable=False)  # 1, 2, 3, etc. within the run
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Analysis results
    analyst_signals = Column(JSON, nullable=True)  # All agent decisions/signals
    trading_decisions = Column(JSON, nullable=True)  # Portfolio manager decisions
    executed_trades = Column(JSON, nullable=True)  # Actual trades executed (paper trading)
    
    # Portfolio state after this cycle
    portfolio_snapshot = Column(JSON, nullable=True)  # Cash, positions, performance metrics
    
    # Performance metrics for this cycle
    performance_metrics = Column(JSON, nullable=True)  # Returns, sharpe ratio, etc.
    
    # Execution tracking
    status = Column(String(50), nullable=False, default="IN_PROGRESS")  # IN_PROGRESS, COMPLETED, ERROR
    error_message = Column(Text, nullable=True)  # Store error details if cycle failed
    
    # Cost tracking
    llm_calls_count = Column(Integer, nullable=True, default=0)  # Number of LLM calls made
    api_calls_count = Column(Integer, nullable=True, default=0)  # Number of financial API calls made
    estimated_cost = Column(String(20), nullable=True)  # Estimated cost in USD
    
    # Metadata
    trigger_reason = Column(String(100), nullable=True)  # scheduled, manual, market_event, etc.
    market_conditions = Column(JSON, nullable=True)  # Market data snapshot at cycle start


class ApiKey(Base):
    """Table to store API keys for various services"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # API key details
    provider = Column(String(100), nullable=False, unique=True, index=True)  # e.g., "ANTHROPIC_API_KEY"
    key_value = Column(Text, nullable=False)  # The actual API key (encrypted in production)
    is_active = Column(Boolean, default=True)  # Enable/disable without deletion
    
    # Optional metadata
    description = Column(Text, nullable=True)  # Human-readable description
    last_used = Column(DateTime(timezone=True), nullable=True)  # Track usage


class HistoricalPrice(Base):
    """Table to store historical OHLCV price data"""
    __tablename__ = "historical_prices"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    # OHLCV data
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data_source = Column(String(50), nullable=False)  # yahoo_finance, financial_datasets, etc.

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_ticker_date', 'ticker', 'date', unique=True),
    )


class StoredFinancialMetrics(Base):
    """Table to store financial metrics data"""
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    report_period = Column(Date, nullable=False, index=True)
    period = Column(String(20), nullable=False)  # TTM, FY, Q1, Q2, etc.
    currency = Column(String(10), nullable=False)

    # Valuation metrics
    market_cap = Column(Float, nullable=True)
    enterprise_value = Column(Float, nullable=True)
    price_to_earnings_ratio = Column(Float, nullable=True)
    price_to_book_ratio = Column(Float, nullable=True)
    price_to_sales_ratio = Column(Float, nullable=True)
    enterprise_value_to_ebitda_ratio = Column(Float, nullable=True)
    enterprise_value_to_revenue_ratio = Column(Float, nullable=True)
    free_cash_flow_yield = Column(Float, nullable=True)
    peg_ratio = Column(Float, nullable=True)

    # Profitability metrics
    gross_margin = Column(Float, nullable=True)
    operating_margin = Column(Float, nullable=True)
    net_margin = Column(Float, nullable=True)
    return_on_equity = Column(Float, nullable=True)
    return_on_assets = Column(Float, nullable=True)
    return_on_invested_capital = Column(Float, nullable=True)

    # Efficiency metrics
    asset_turnover = Column(Float, nullable=True)
    inventory_turnover = Column(Float, nullable=True)
    receivables_turnover = Column(Float, nullable=True)
    days_sales_outstanding = Column(Float, nullable=True)
    operating_cycle = Column(Float, nullable=True)
    working_capital_turnover = Column(Float, nullable=True)

    # Liquidity metrics
    current_ratio = Column(Float, nullable=True)
    quick_ratio = Column(Float, nullable=True)
    cash_ratio = Column(Float, nullable=True)
    operating_cash_flow_ratio = Column(Float, nullable=True)

    # Leverage metrics
    debt_to_equity = Column(Float, nullable=True)
    debt_to_assets = Column(Float, nullable=True)
    interest_coverage = Column(Float, nullable=True)

    # Growth metrics
    revenue_growth = Column(Float, nullable=True)
    earnings_growth = Column(Float, nullable=True)
    book_value_growth = Column(Float, nullable=True)
    earnings_per_share_growth = Column(Float, nullable=True)
    free_cash_flow_growth = Column(Float, nullable=True)
    operating_income_growth = Column(Float, nullable=True)
    ebitda_growth = Column(Float, nullable=True)

    # Per-share metrics
    payout_ratio = Column(Float, nullable=True)
    earnings_per_share = Column(Float, nullable=True)
    book_value_per_share = Column(Float, nullable=True)
    free_cash_flow_per_share = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data_source = Column(String(50), nullable=False)

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_ticker_report_period', 'ticker', 'report_period', 'period', unique=True),
    )


class StoredCompanyNews(Base):
    """Table to store company news articles"""
    __tablename__ = "company_news"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    title = Column(Text, nullable=False)
    author = Column(String(200), nullable=True)
    source = Column(String(200), nullable=False)
    date = Column(Date, nullable=False, index=True)
    url = Column(Text, nullable=False)
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data_source = Column(String(50), nullable=False)

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_ticker_date_news', 'ticker', 'date'),
        Index('idx_url_unique', 'url', unique=True),
    )


class StoredInsiderTrade(Base):
    """Table to store insider trading data"""
    __tablename__ = "insider_trades"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)
    issuer = Column(String(200), nullable=True)
    name = Column(String(200), nullable=True)
    title = Column(String(200), nullable=True)
    is_board_director = Column(Boolean, nullable=True)

    # Transaction details
    transaction_date = Column(Date, nullable=True, index=True)
    transaction_shares = Column(Float, nullable=True)
    transaction_price_per_share = Column(Float, nullable=True)
    transaction_value = Column(Float, nullable=True)
    shares_owned_before_transaction = Column(Float, nullable=True)
    shares_owned_after_transaction = Column(Float, nullable=True)
    security_title = Column(String(200), nullable=True)
    filing_date = Column(Date, nullable=False, index=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    data_source = Column(String(50), nullable=False)

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_ticker_filing_date', 'ticker', 'filing_date'),
        Index('idx_ticker_transaction_date', 'ticker', 'transaction_date'),
    )


class BacktestRun(Base):
    """Table to store backtest execution runs with key metrics"""
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Run metadata
    name = Column(String(200), nullable=True)  # Optional user-provided name
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="IDLE", index=True)  # IDLE, IN_PROGRESS, COMPLETE, ERROR

    # Backtest parameters
    tickers = Column(JSON, nullable=False)  # Array of ticker symbols
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    initial_capital = Column(Float, nullable=False)

    # Performance metrics (summary)
    final_portfolio_value = Column(Float, nullable=True)
    total_return_pct = Column(Float, nullable=True)  # Percentage return
    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)  # Percentage
    max_drawdown_date = Column(Date, nullable=True)
    long_short_ratio = Column(Float, nullable=True)
    gross_exposure = Column(Float, nullable=True)
    net_exposure = Column(Float, nullable=True)

    # Configuration (stored as JSON for flexibility)
    graph_config = Column(JSON, nullable=True)  # Nodes and edges
    agent_models = Column(JSON, nullable=True)  # Agent model configurations
    request_data = Column(JSON, nullable=True)  # Full request parameters
    final_portfolio = Column(JSON, nullable=True)  # Final portfolio state (positions, cash, etc.)

    # Error tracking
    error_message = Column(Text, nullable=True)

    # Indexes for efficient queries
    __table_args__ = (
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_date_range', 'start_date', 'end_date'),
    )


class BacktestDailyResult(Base):
    """Table to store daily results for each backtest run"""
    __tablename__ = "backtest_daily_results"

    id = Column(Integer, primary_key=True, index=True)
    backtest_run_id = Column(Integer, ForeignKey("backtest_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    # Portfolio state
    portfolio_value = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)

    # Trading activity (stored as JSON)
    decisions = Column(JSON, nullable=True)  # Trading decisions made
    executed_trades = Column(JSON, nullable=True)  # Actual trades executed
    analyst_signals = Column(JSON, nullable=True)  # Agent signals/analysis
    current_prices = Column(JSON, nullable=True)  # Prices for all tickers

    # Exposure metrics
    long_exposure = Column(Float, nullable=True)
    short_exposure = Column(Float, nullable=True)
    gross_exposure = Column(Float, nullable=True)
    net_exposure = Column(Float, nullable=True)
    long_short_ratio = Column(Float, nullable=True)

    # Performance metrics
    portfolio_return_pct = Column(Float, nullable=True)  # Cumulative return percentage

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_backtest_date', 'backtest_run_id', 'date', unique=True),
    )


