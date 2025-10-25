"""
Data acquisition module for fetching and persisting market data to database.
This module separates data fetching from analysis, allowing backtests to use cached data.
"""
from datetime import datetime, date
from typing import Optional
import sys
from pathlib import Path

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
    print("Warning: Database modules not available. Data acquisition requires database dependencies.")

from ..tools.api import (
    get_prices,
    get_financial_metrics as api_get_financial_metrics,
    get_insider_trades as api_get_insider_trades,
    get_company_news as api_get_company_news
)
from ..tools.api_config import get_api_provider


def _parse_date(date_str: str) -> date:
    """Parse date string to date object"""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def acquire_prices(ticker: str, start_date: str, end_date: str, force_refresh: bool = False) -> int:
    """
    Fetch and persist historical price data to database.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        force_refresh: If True, re-fetch and update existing data

    Returns:
        Number of price records saved
    """
    if not DATABASE_AVAILABLE:
        raise RuntimeError("Database is not available. Please install required dependencies.")

    db = SessionLocal()
    try:
        # Check if data already exists
        if not force_refresh:
            existing_count = db.query(HistoricalPrice).filter(
                HistoricalPrice.ticker == ticker,
                HistoricalPrice.date >= _parse_date(start_date),
                HistoricalPrice.date <= _parse_date(end_date)
            ).count()

            if existing_count > 0:
                print(f"  {ticker}: {existing_count} price records already exist (use force_refresh=True to update)")
                return 0

        # Fetch data from API
        print(f"  {ticker}: Fetching prices from {start_date} to {end_date}...")
        prices = get_prices(ticker, start_date, end_date)

        if not prices:
            print(f"  {ticker}: No price data available")
            return 0

        # Get data source
        data_source = get_api_provider()

        # Persist to database
        saved_count = 0
        for price in prices:
            price_date = _parse_date(price.time)

            # Check if record exists
            existing = db.query(HistoricalPrice).filter(
                HistoricalPrice.ticker == ticker,
                HistoricalPrice.date == price_date
            ).first()

            if existing:
                if force_refresh:
                    # Update existing record
                    existing.open = price.open
                    existing.high = price.high
                    existing.low = price.low
                    existing.close = price.close
                    existing.volume = price.volume
                    existing.data_source = data_source
                    saved_count += 1
            else:
                # Create new record
                db_price = HistoricalPrice(
                    ticker=ticker,
                    date=price_date,
                    open=price.open,
                    high=price.high,
                    low=price.low,
                    close=price.close,
                    volume=price.volume,
                    data_source=data_source
                )
                db.add(db_price)
                saved_count += 1

        db.commit()
        print(f"  {ticker}: Saved {saved_count} price records")
        return saved_count

    except Exception as e:
        db.rollback()
        print(f"  {ticker}: Error acquiring prices: {e}")
        raise
    finally:
        db.close()


def acquire_financial_metrics(ticker: str, report_date: str, force_refresh: bool = False) -> int:
    """
    Fetch and persist financial metrics to database.

    Args:
        ticker: Stock ticker symbol
        report_date: Report date in YYYY-MM-DD format
        force_refresh: If True, re-fetch and update existing data

    Returns:
        Number of metric records saved
    """
    if not DATABASE_AVAILABLE:
        raise RuntimeError("Database is not available. Please install required dependencies.")

    db = SessionLocal()
    try:
        # Fetch data from API
        print(f"  {ticker}: Fetching financial metrics as of {report_date}...")
        metrics_list = api_get_financial_metrics(ticker, report_date)

        if not metrics_list:
            print(f"  {ticker}: No financial metrics available")
            return 0

        # Get data source
        data_source = get_api_provider()

        # Persist to database
        saved_count = 0
        for metrics in metrics_list:
            report_period = _parse_date(metrics.report_period)

            # Check if record exists
            existing = db.query(StoredFinancialMetrics).filter(
                StoredFinancialMetrics.ticker == ticker,
                StoredFinancialMetrics.report_period == report_period,
                StoredFinancialMetrics.period == metrics.period
            ).first()

            if existing and not force_refresh:
                continue

            if existing:
                # Update existing record
                for field, value in metrics.model_dump().items():
                    if field not in ['ticker', 'report_period', 'period']:
                        setattr(existing, field, value)
                existing.data_source = data_source
                saved_count += 1
            else:
                # Create new record
                db_metrics = StoredFinancialMetrics(
                    ticker=metrics.ticker,
                    report_period=report_period,
                    period=metrics.period,
                    currency=metrics.currency,
                    market_cap=metrics.market_cap,
                    enterprise_value=metrics.enterprise_value,
                    price_to_earnings_ratio=metrics.price_to_earnings_ratio,
                    price_to_book_ratio=metrics.price_to_book_ratio,
                    price_to_sales_ratio=metrics.price_to_sales_ratio,
                    enterprise_value_to_ebitda_ratio=metrics.enterprise_value_to_ebitda_ratio,
                    enterprise_value_to_revenue_ratio=metrics.enterprise_value_to_revenue_ratio,
                    free_cash_flow_yield=metrics.free_cash_flow_yield,
                    peg_ratio=metrics.peg_ratio,
                    gross_margin=metrics.gross_margin,
                    operating_margin=metrics.operating_margin,
                    net_margin=metrics.net_margin,
                    return_on_equity=metrics.return_on_equity,
                    return_on_assets=metrics.return_on_assets,
                    return_on_invested_capital=metrics.return_on_invested_capital,
                    asset_turnover=metrics.asset_turnover,
                    inventory_turnover=metrics.inventory_turnover,
                    receivables_turnover=metrics.receivables_turnover,
                    days_sales_outstanding=metrics.days_sales_outstanding,
                    operating_cycle=metrics.operating_cycle,
                    working_capital_turnover=metrics.working_capital_turnover,
                    current_ratio=metrics.current_ratio,
                    quick_ratio=metrics.quick_ratio,
                    cash_ratio=metrics.cash_ratio,
                    operating_cash_flow_ratio=metrics.operating_cash_flow_ratio,
                    debt_to_equity=metrics.debt_to_equity,
                    debt_to_assets=metrics.debt_to_assets,
                    interest_coverage=metrics.interest_coverage,
                    revenue_growth=metrics.revenue_growth,
                    earnings_growth=metrics.earnings_growth,
                    book_value_growth=metrics.book_value_growth,
                    earnings_per_share_growth=metrics.earnings_per_share_growth,
                    free_cash_flow_growth=metrics.free_cash_flow_growth,
                    operating_income_growth=metrics.operating_income_growth,
                    ebitda_growth=metrics.ebitda_growth,
                    payout_ratio=metrics.payout_ratio,
                    earnings_per_share=metrics.earnings_per_share,
                    book_value_per_share=metrics.book_value_per_share,
                    free_cash_flow_per_share=metrics.free_cash_flow_per_share,
                    data_source=data_source
                )
                db.add(db_metrics)
                saved_count += 1

        db.commit()
        print(f"  {ticker}: Saved {saved_count} financial metric records")
        return saved_count

    except Exception as e:
        db.rollback()
        print(f"  {ticker}: Error acquiring financial metrics: {e}")
        raise
    finally:
        db.close()


def acquire_company_news(ticker: str, start_date: str, end_date: str, force_refresh: bool = False) -> int:
    """
    Fetch and persist company news to database.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        force_refresh: If True, re-fetch and update existing data

    Returns:
        Number of news records saved
    """
    if not DATABASE_AVAILABLE:
        raise RuntimeError("Database is not available. Please install required dependencies.")

    db = SessionLocal()
    try:
        # Fetch data from API
        print(f"  {ticker}: Fetching company news from {start_date} to {end_date}...")
        news_list = api_get_company_news(ticker, end_date, start_date)

        if not news_list:
            print(f"  {ticker}: No company news available")
            return 0

        # Get data source
        data_source = get_api_provider()

        # Persist to database
        saved_count = 0
        for news in news_list:
            news_date = _parse_date(news.date)

            # Check if record exists by URL (unique)
            existing = db.query(StoredCompanyNews).filter(
                StoredCompanyNews.url == news.url
            ).first()

            if existing and not force_refresh:
                continue

            if existing:
                # Update existing record
                existing.ticker = news.ticker
                existing.title = news.title
                existing.author = news.author
                existing.source = news.source
                existing.date = news_date
                existing.sentiment = news.sentiment
                existing.data_source = data_source
                saved_count += 1
            else:
                # Create new record
                db_news = StoredCompanyNews(
                    ticker=news.ticker,
                    title=news.title,
                    author=news.author,
                    source=news.source,
                    date=news_date,
                    url=news.url,
                    sentiment=news.sentiment,
                    data_source=data_source
                )
                db.add(db_news)
                saved_count += 1

        db.commit()
        print(f"  {ticker}: Saved {saved_count} news records")
        return saved_count

    except Exception as e:
        db.rollback()
        print(f"  {ticker}: Error acquiring company news: {e}")
        raise
    finally:
        db.close()


def acquire_insider_trades(ticker: str, start_date: str, end_date: str, force_refresh: bool = False) -> int:
    """
    Fetch and persist insider trades to database.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        force_refresh: If True, re-fetch and update existing data

    Returns:
        Number of insider trade records saved
    """
    if not DATABASE_AVAILABLE:
        raise RuntimeError("Database is not available. Please install required dependencies.")

    db = SessionLocal()
    try:
        # Fetch data from API
        print(f"  {ticker}: Fetching insider trades from {start_date} to {end_date}...")
        trades_list = api_get_insider_trades(ticker, end_date, start_date)

        if not trades_list:
            print(f"  {ticker}: No insider trades available")
            return 0

        # Get data source
        data_source = get_api_provider()

        # Persist to database
        saved_count = 0
        for trade in trades_list:
            filing_date = _parse_date(trade.filing_date)
            transaction_date = _parse_date(trade.transaction_date) if trade.transaction_date else None

            # Check if similar record exists
            existing = db.query(StoredInsiderTrade).filter(
                StoredInsiderTrade.ticker == ticker,
                StoredInsiderTrade.filing_date == filing_date,
                StoredInsiderTrade.name == trade.name,
                StoredInsiderTrade.transaction_date == transaction_date
            ).first()

            if existing and not force_refresh:
                continue

            if existing:
                # Update existing record
                existing.issuer = trade.issuer
                existing.title = trade.title
                existing.is_board_director = trade.is_board_director
                existing.transaction_shares = trade.transaction_shares
                existing.transaction_price_per_share = trade.transaction_price_per_share
                existing.transaction_value = trade.transaction_value
                existing.shares_owned_before_transaction = trade.shares_owned_before_transaction
                existing.shares_owned_after_transaction = trade.shares_owned_after_transaction
                existing.security_title = trade.security_title
                existing.data_source = data_source
                saved_count += 1
            else:
                # Create new record
                db_trade = StoredInsiderTrade(
                    ticker=trade.ticker,
                    issuer=trade.issuer,
                    name=trade.name,
                    title=trade.title,
                    is_board_director=trade.is_board_director,
                    transaction_date=transaction_date,
                    transaction_shares=trade.transaction_shares,
                    transaction_price_per_share=trade.transaction_price_per_share,
                    transaction_value=trade.transaction_value,
                    shares_owned_before_transaction=trade.shares_owned_before_transaction,
                    shares_owned_after_transaction=trade.shares_owned_after_transaction,
                    security_title=trade.security_title,
                    filing_date=filing_date,
                    data_source=data_source
                )
                db.add(db_trade)
                saved_count += 1

        db.commit()
        print(f"  {ticker}: Saved {saved_count} insider trade records")
        return saved_count

    except Exception as e:
        db.rollback()
        print(f"  {ticker}: Error acquiring insider trades: {e}")
        raise
    finally:
        db.close()


def acquire_all_data(
    tickers: list[str],
    start_date: str,
    end_date: str,
    include_prices: bool = True,
    include_metrics: bool = True,
    include_news: bool = True,
    include_insider_trades: bool = True,
    force_refresh: bool = False
) -> dict[str, dict[str, int]]:
    """
    Acquire all market data for multiple tickers.

    Args:
        tickers: List of stock ticker symbols
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        include_prices: Whether to fetch price data
        include_metrics: Whether to fetch financial metrics
        include_news: Whether to fetch company news
        include_insider_trades: Whether to fetch insider trades
        force_refresh: If True, re-fetch and update existing data

    Returns:
        Dictionary mapping ticker to counts of saved records by type
    """
    results = {}

    print(f"\nAcquiring data for {len(tickers)} tickers from {start_date} to {end_date}")
    print(f"Data source: {get_api_provider()}")
    print("=" * 70)

    for ticker in tickers:
        print(f"\n{ticker}:")
        ticker_results = {}

        try:
            if include_prices:
                ticker_results['prices'] = acquire_prices(ticker, start_date, end_date, force_refresh)

            if include_metrics:
                ticker_results['metrics'] = acquire_financial_metrics(ticker, end_date, force_refresh)

            if include_news:
                ticker_results['news'] = acquire_company_news(ticker, start_date, end_date, force_refresh)

            if include_insider_trades:
                ticker_results['insider_trades'] = acquire_insider_trades(ticker, start_date, end_date, force_refresh)

            results[ticker] = ticker_results

        except Exception as e:
            print(f"  {ticker}: Failed - {e}")
            results[ticker] = {'error': str(e)}

    print("\n" + "=" * 70)
    print("Data acquisition complete!")
    print(f"Successfully processed {len([r for r in results.values() if 'error' not in r])}/{len(tickers)} tickers")

    return results
