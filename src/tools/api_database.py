"""
Database API implementation that loads cached market data from SQLite database.
Provides the same interface as api.py but reads from database instead of external APIs.
"""
from datetime import datetime, date
import sys
from pathlib import Path
from typing import Optional

# Add backend to path for database imports
backend_path = Path(__file__).parent.parent.parent / "app" / "backend"
sys.path.insert(0, str(backend_path))

try:
    from database.connection import SessionLocal
    from database.models import (
        HistoricalPrice,
        StoredFinancialMetrics,
        StoredCompanyNews,
        StoredInsiderTrade
    )
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

from ..data.models import (
    Price,
    FinancialMetrics,
    CompanyNews,
    InsiderTrade
)


def _parse_date(date_input: str | date) -> date:
    """Parse date string or date object to date"""
    if isinstance(date_input, date):
        return date_input
    return datetime.strptime(date_input, "%Y-%m-%d").date()


def _format_date(date_obj: date) -> str:
    """Format date object to YYYY-MM-DD string"""
    return date_obj.strftime("%Y-%m-%d")


def get_prices(ticker: str, start_date: str, end_date: str, api_key: Optional[str] = None) -> list[Price]:
    """
    Get historical OHLCV prices from database.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        api_key: Ignored (for interface compatibility)

    Returns:
        List of Price objects
    """
    if not DATABASE_AVAILABLE:
        raise RuntimeError("Database is not available. Run data acquisition first.")

    db = SessionLocal()
    try:
        start = _parse_date(start_date)
        end = _parse_date(end_date)

        db_prices = db.query(HistoricalPrice).filter(
            HistoricalPrice.ticker == ticker,
            HistoricalPrice.date >= start,
            HistoricalPrice.date <= end
        ).order_by(HistoricalPrice.date).all()

        if not db_prices:
            print(f"Warning: No price data found in database for {ticker} from {start_date} to {end_date}")
            return []

        # Convert to Price objects
        prices = [
            Price(
                open=p.open,
                close=p.close,
                high=p.high,
                low=p.low,
                volume=p.volume,
                time=_format_date(p.date)
            )
            for p in db_prices
        ]

        return prices

    finally:
        db.close()


def get_financial_metrics(
    ticker: str,
    end_date: str,
    period: Optional[str] = None,
    limit: Optional[int] = None,
    api_key: Optional[str] = None
) -> list[FinancialMetrics]:
    """
    Get financial metrics from database.

    Args:
        ticker: Stock ticker symbol
        end_date: End date in YYYY-MM-DD format
        period: Period type (e.g., 'TTM', 'FY', 'Q1', etc.)
        limit: Maximum number of records to return
        api_key: Ignored (for interface compatibility)

    Returns:
        List of FinancialMetrics objects
    """
    if not DATABASE_AVAILABLE:
        raise RuntimeError("Database is not available. Run data acquisition first.")

    db = SessionLocal()
    try:
        end = _parse_date(end_date)

        query = db.query(StoredFinancialMetrics).filter(
            StoredFinancialMetrics.ticker == ticker,
            StoredFinancialMetrics.report_period <= end
        )

        if period:
            query = query.filter(StoredFinancialMetrics.period == period)

        query = query.order_by(StoredFinancialMetrics.report_period.desc())

        if limit:
            query = query.limit(limit)

        db_metrics = query.all()

        if not db_metrics:
            print(f"Warning: No financial metrics found in database for {ticker} as of {end_date}")
            return []

        # Convert to FinancialMetrics objects
        metrics = [
            FinancialMetrics(
                ticker=m.ticker,
                report_period=_format_date(m.report_period),
                period=m.period,
                currency=m.currency,
                market_cap=m.market_cap,
                enterprise_value=m.enterprise_value,
                price_to_earnings_ratio=m.price_to_earnings_ratio,
                price_to_book_ratio=m.price_to_book_ratio,
                price_to_sales_ratio=m.price_to_sales_ratio,
                enterprise_value_to_ebitda_ratio=m.enterprise_value_to_ebitda_ratio,
                enterprise_value_to_revenue_ratio=m.enterprise_value_to_revenue_ratio,
                free_cash_flow_yield=m.free_cash_flow_yield,
                peg_ratio=m.peg_ratio,
                gross_margin=m.gross_margin,
                operating_margin=m.operating_margin,
                net_margin=m.net_margin,
                return_on_equity=m.return_on_equity,
                return_on_assets=m.return_on_assets,
                return_on_invested_capital=m.return_on_invested_capital,
                asset_turnover=m.asset_turnover,
                inventory_turnover=m.inventory_turnover,
                receivables_turnover=m.receivables_turnover,
                days_sales_outstanding=m.days_sales_outstanding,
                operating_cycle=m.operating_cycle,
                working_capital_turnover=m.working_capital_turnover,
                current_ratio=m.current_ratio,
                quick_ratio=m.quick_ratio,
                cash_ratio=m.cash_ratio,
                operating_cash_flow_ratio=m.operating_cash_flow_ratio,
                debt_to_equity=m.debt_to_equity,
                debt_to_assets=m.debt_to_assets,
                interest_coverage=m.interest_coverage,
                revenue_growth=m.revenue_growth,
                earnings_growth=m.earnings_growth,
                book_value_growth=m.book_value_growth,
                earnings_per_share_growth=m.earnings_per_share_growth,
                free_cash_flow_growth=m.free_cash_flow_growth,
                operating_income_growth=m.operating_income_growth,
                ebitda_growth=m.ebitda_growth,
                payout_ratio=m.payout_ratio,
                earnings_per_share=m.earnings_per_share,
                book_value_per_share=m.book_value_per_share,
                free_cash_flow_per_share=m.free_cash_flow_per_share
            )
            for m in db_metrics
        ]

        return metrics

    finally:
        db.close()


def get_company_news(
    ticker: str,
    end_date: str,
    start_date: Optional[str] = None,
    api_key: Optional[str] = None
) -> list[CompanyNews]:
    """
    Get company news from database.

    Args:
        ticker: Stock ticker symbol
        end_date: End date in YYYY-MM-DD format
        start_date: Start date in YYYY-MM-DD format (optional)
        api_key: Ignored (for interface compatibility)

    Returns:
        List of CompanyNews objects
    """
    if not DATABASE_AVAILABLE:
        raise RuntimeError("Database is not available. Run data acquisition first.")

    db = SessionLocal()
    try:
        end = _parse_date(end_date)

        query = db.query(StoredCompanyNews).filter(
            StoredCompanyNews.ticker == ticker,
            StoredCompanyNews.date <= end
        )

        if start_date:
            start = _parse_date(start_date)
            query = query.filter(StoredCompanyNews.date >= start)

        db_news = query.order_by(StoredCompanyNews.date.desc()).all()

        if not db_news:
            print(f"Warning: No company news found in database for {ticker}")
            return []

        # Convert to CompanyNews objects
        news = [
            CompanyNews(
                ticker=n.ticker,
                title=n.title,
                author=n.author or "",
                source=n.source,
                date=_format_date(n.date),
                url=n.url,
                sentiment=n.sentiment
            )
            for n in db_news
        ]

        return news

    finally:
        db.close()


def get_insider_trades(
    ticker: str,
    end_date: str,
    start_date: Optional[str] = None,
    api_key: Optional[str] = None
) -> list[InsiderTrade]:
    """
    Get insider trades from database.

    Args:
        ticker: Stock ticker symbol
        end_date: End date in YYYY-MM-DD format
        start_date: Start date in YYYY-MM-DD format (optional)
        api_key: Ignored (for interface compatibility)

    Returns:
        List of InsiderTrade objects
    """
    if not DATABASE_AVAILABLE:
        raise RuntimeError("Database is not available. Run data acquisition first.")

    db = SessionLocal()
    try:
        end = _parse_date(end_date)

        query = db.query(StoredInsiderTrade).filter(
            StoredInsiderTrade.ticker == ticker,
            StoredInsiderTrade.filing_date <= end
        )

        if start_date:
            start = _parse_date(start_date)
            query = query.filter(StoredInsiderTrade.filing_date >= start)

        db_trades = query.order_by(StoredInsiderTrade.filing_date.desc()).all()

        if not db_trades:
            # Insider trades may legitimately not exist for many stocks
            return []

        # Convert to InsiderTrade objects
        trades = [
            InsiderTrade(
                ticker=t.ticker,
                issuer=t.issuer,
                name=t.name,
                title=t.title,
                is_board_director=t.is_board_director,
                transaction_date=_format_date(t.transaction_date) if t.transaction_date else None,
                transaction_shares=t.transaction_shares,
                transaction_price_per_share=t.transaction_price_per_share,
                transaction_value=t.transaction_value,
                shares_owned_before_transaction=t.shares_owned_before_transaction,
                shares_owned_after_transaction=t.shares_owned_after_transaction,
                security_title=t.security_title,
                filing_date=_format_date(t.filing_date)
            )
            for t in db_trades
        ]

        return trades

    finally:
        db.close()


def get_price_data(ticker: str, start_date: str, end_date: str, api_key: Optional[str] = None):
    """
    Get historical price data as pandas DataFrame from database.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        api_key: Ignored (for interface compatibility)

    Returns:
        pandas DataFrame with OHLCV data
    """
    import pandas as pd

    prices = get_prices(ticker, start_date, end_date, api_key)

    if not prices:
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame([p.model_dump() for p in prices])
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    df.index.name = 'Date'

    return df
