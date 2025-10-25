#!/usr/bin/env python3
"""
Data Acquisition CLI

Fetch and cache market data to the database for later use in backtesting.
This separates data acquisition from analysis, avoiding repeated API calls.

Usage:
    python -m src.acquire_data --tickers AAPL MSFT --start-date 2020-01-01 --end-date 2024-12-31
    python -m src.acquire_data --tickers AAPL --start-date 2023-01-01 --end-date 2023-12-31 --force-refresh
"""

import argparse
from datetime import datetime, timedelta
import os
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data.acquisition import acquire_all_data
from src.tools.api_config import print_api_info, get_api_provider


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Acquire and cache market data for backtesting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Acquire 1 year of data for AAPL and MSFT
  python -m src.acquire_data --tickers AAPL MSFT --start-date 2023-01-01 --end-date 2023-12-31

  # Acquire 5 years of data with forced refresh
  python -m src.acquire_data --tickers AAPL --start-date 2019-01-01 --end-date 2023-12-31 --force-refresh

  # Acquire only prices (skip metrics, news, insider trades)
  python -m src.acquire_data --tickers AAPL --start-date 2023-01-01 --end-date 2023-12-31 --prices-only

  # Use Yahoo Finance as data source
  USE_YAHOO_FINANCE=true python -m src.acquire_data --tickers AAPL --start-date 2023-01-01 --end-date 2023-12-31

Environment Variables:
  USE_YAHOO_FINANCE=true     Use Yahoo Finance API (free)
  (default)                   Use Financial Datasets API (paid)
        """
    )

    parser.add_argument(
        "--tickers",
        nargs="+",
        required=True,
        help="Stock ticker symbols (e.g., AAPL MSFT GOOGL)"
    )

    parser.add_argument(
        "--start-date",
        required=True,
        help="Start date in YYYY-MM-DD format"
    )

    parser.add_argument(
        "--end-date",
        help="End date in YYYY-MM-DD format (defaults to today)"
    )

    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Re-fetch and update existing data"
    )

    parser.add_argument(
        "--prices-only",
        action="store_true",
        help="Only acquire price data (skip metrics, news, insider trades)"
    )

    parser.add_argument(
        "--no-prices",
        action="store_true",
        help="Skip price data acquisition"
    )

    parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="Skip financial metrics acquisition"
    )

    parser.add_argument(
        "--no-news",
        action="store_true",
        help="Skip company news acquisition"
    )

    parser.add_argument(
        "--no-insider-trades",
        action="store_true",
        help="Skip insider trades acquisition"
    )

    return parser.parse_args()


def validate_date(date_str: str) -> bool:
    """Validate date format"""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def main():
    """Main entry point"""
    args = parse_args()

    # Validate dates
    if not validate_date(args.start_date):
        print(f"Error: Invalid start date format: {args.start_date}")
        print("Expected format: YYYY-MM-DD")
        sys.exit(1)

    end_date = args.end_date
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    elif not validate_date(end_date):
        print(f"Error: Invalid end date format: {end_date}")
        print("Expected format: YYYY-MM-DD")
        sys.exit(1)

    # Check if start date is before end date
    start = datetime.strptime(args.start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    if start > end:
        print("Error: Start date must be before end date")
        sys.exit(1)

    # Check if using database mode (shouldn't be)
    if get_api_provider() == "database":
        print("\n⚠️  Warning: USE_DATABASE is set to true.")
        print("Data acquisition requires an external API (Yahoo Finance or Financial Datasets).")
        print("Please unset USE_DATABASE or set USE_YAHOO_FINANCE=true to acquire data.")
        print("\nExample:")
        print("  USE_YAHOO_FINANCE=true python -m src.acquire_data --tickers AAPL --start-date 2023-01-01 --end-date 2023-12-31\n")
        sys.exit(1)

    # Print configuration
    print("\n" + "="*70)
    print("Data Acquisition Configuration")
    print("="*70)
    print(f"Tickers: {', '.join(args.tickers)}")
    print(f"Date Range: {args.start_date} to {end_date}")
    print(f"Force Refresh: {args.force_refresh}")
    print()
    print_api_info()

    # Determine what to acquire
    if args.prices_only:
        include_prices = True
        include_metrics = False
        include_news = False
        include_insider_trades = False
    else:
        include_prices = not args.no_prices
        include_metrics = not args.no_metrics
        include_news = not args.no_news
        include_insider_trades = not args.no_insider_trades

    print("Data to acquire:")
    print(f"  {'✅' if include_prices else '❌'} Historical Prices")
    print(f"  {'✅' if include_metrics else '❌'} Financial Metrics")
    print(f"  {'✅' if include_news else '❌'} Company News")
    print(f"  {'✅' if include_insider_trades else '❌'} Insider Trades")
    print()

    # Confirm before proceeding
    response = input("Proceed with data acquisition? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Cancelled.")
        sys.exit(0)

    # Acquire data
    try:
        results = acquire_all_data(
            tickers=args.tickers,
            start_date=args.start_date,
            end_date=end_date,
            include_prices=include_prices,
            include_metrics=include_metrics,
            include_news=include_news,
            include_insider_trades=include_insider_trades,
            force_refresh=args.force_refresh
        )

        # Print summary
        print("\n" + "="*70)
        print("Summary")
        print("="*70)
        for ticker, counts in results.items():
            if 'error' in counts:
                print(f"{ticker}: ❌ Failed - {counts['error']}")
            else:
                print(f"{ticker}:")
                if 'prices' in counts:
                    print(f"  Prices: {counts['prices']} records")
                if 'metrics' in counts:
                    print(f"  Metrics: {counts['metrics']} records")
                if 'news' in counts:
                    print(f"  News: {counts['news']} records")
                if 'insider_trades' in counts:
                    print(f"  Insider Trades: {counts['insider_trades']} records")

        print("\n✅ Data acquisition complete!")
        print("\nYou can now run backtests with USE_DATABASE=true to use this cached data.")
        print("Example:")
        print(f"  USE_DATABASE=true python -m src.backtester --tickers {' '.join(args.tickers)} --start-date {args.start_date} --end-date {end_date}\n")

    except Exception as e:
        print(f"\n❌ Error during data acquisition: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
