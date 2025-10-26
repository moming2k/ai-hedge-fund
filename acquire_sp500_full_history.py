#!/usr/bin/env python3
"""
Acquire complete historical data for all S&P 500 companies from 1999 to today.

This script:
1. Loads S&P 500 ticker list from data/sp500.csv
2. For each company, acquires:
   - Historical prices (OHLCV) from 1999-01-01 to today
   - Financial metrics
   - Company news (where available)
   - Insider trades (where available)
   - Financial statement line items (Income Statement, Balance Sheet, Cash Flow)
3. Stores all data in PostgreSQL database
4. Provides progress tracking and error handling
5. Resumes from where it left off if interrupted
"""

import sys
import pandas as pd
from datetime import datetime, date
import time
import os

# Set environment variables for Yahoo Finance mode
os.environ['USE_YAHOO_FINANCE'] = 'true'

# Add project root to path
sys.path.insert(0, '/Users/moming2k/project/ai-hedge-fund')

from src.data.acquisition import acquire_all_data

def main():
    # Configuration
    start_date = "1999-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    print("=" * 80)
    print("S&P 500 FULL HISTORICAL DATA ACQUISITION")
    print("=" * 80)
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Data Types: Prices, Metrics, News, Insider Trades, Line Items")
    print("=" * 80)

    # Load S&P 500 tickers
    try:
        sp500_df = pd.read_csv('data/sp500.csv')
        # Clean tickers (replace . with -)
        tickers = [t.replace('.', '-') for t in sp500_df['ticker'].tolist()]
        print(f"\n✅ Loaded {len(tickers)} S&P 500 tickers from data/sp500.csv")
    except Exception as e:
        print(f"\n❌ Error loading S&P 500 tickers: {e}")
        print("Please ensure data/sp500.csv exists")
        return 1

    # Create progress tracking file
    progress_file = 'data/acquisition_progress.txt'
    completed_tickers = set()

    # Load previously completed tickers
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            completed_tickers = set(line.strip() for line in f if line.strip())
        print(f"📋 Found {len(completed_tickers)} previously completed tickers")

    # Filter out completed tickers
    remaining_tickers = [t for t in tickers if t not in completed_tickers]

    if not remaining_tickers:
        print("\n✅ All tickers have been processed!")
        return 0

    print(f"📊 Processing {len(remaining_tickers)} remaining tickers")
    print(f"⏱️  Estimated time: {len(remaining_tickers) * 2} - {len(remaining_tickers) * 5} minutes")
    print("\nStarting acquisition...\n")

    # Process tickers in batches
    batch_size = 10
    total_batches = (len(remaining_tickers) + batch_size - 1) // batch_size

    start_time = time.time()
    successful_count = 0
    failed_count = 0
    failed_tickers = []

    for batch_num in range(total_batches):
        batch_start = batch_num * batch_size
        batch_end = min(batch_start + batch_size, len(remaining_tickers))
        batch_tickers = remaining_tickers[batch_start:batch_end]

        print(f"\n{'=' * 80}")
        print(f"BATCH {batch_num + 1}/{total_batches} ({batch_start + 1}-{batch_end}/{len(remaining_tickers)})")
        print(f"{'=' * 80}")

        # Acquire data for batch
        try:
            results = acquire_all_data(
                tickers=batch_tickers,
                start_date=start_date,
                end_date=end_date,
                include_prices=True,
                include_metrics=True,
                include_news=True,
                include_insider_trades=True,
                include_line_items=True,
                force_refresh=False
            )

            # Track successful tickers
            for ticker, result in results.items():
                if 'error' not in result:
                    successful_count += 1
                    completed_tickers.add(ticker)

                    # Append to progress file
                    with open(progress_file, 'a') as f:
                        f.write(f"{ticker}\n")
                else:
                    failed_count += 1
                    failed_tickers.append(ticker)

            # Progress summary
            elapsed_time = time.time() - start_time
            avg_time_per_ticker = elapsed_time / (successful_count + failed_count) if (successful_count + failed_count) > 0 else 0
            remaining = len(remaining_tickers) - (successful_count + failed_count)
            estimated_remaining = remaining * avg_time_per_ticker

            print(f"\n{'=' * 80}")
            print(f"PROGRESS SUMMARY")
            print(f"{'=' * 80}")
            print(f"Completed: {successful_count + failed_count}/{len(remaining_tickers)} tickers")
            print(f"  ✅ Successful: {successful_count}")
            print(f"  ❌ Failed: {failed_count}")
            print(f"⏱️  Elapsed: {elapsed_time / 60:.1f} minutes")
            print(f"⏱️  Avg per ticker: {avg_time_per_ticker:.1f} seconds")
            print(f"⏱️  Estimated remaining: {estimated_remaining / 60:.1f} minutes")

        except Exception as e:
            print(f"\n❌ Batch {batch_num + 1} failed: {e}")
            failed_count += len(batch_tickers)
            failed_tickers.extend(batch_tickers)

        # Small delay between batches to avoid rate limiting
        if batch_num < total_batches - 1:
            time.sleep(2)

    # Final summary
    total_time = time.time() - start_time
    print(f"\n{'=' * 80}")
    print(f"ACQUISITION COMPLETE!")
    print(f"{'=' * 80}")
    print(f"Total tickers processed: {successful_count + failed_count}")
    print(f"  ✅ Successful: {successful_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"⏱️  Total time: {total_time / 60:.1f} minutes")
    print(f"⏱️  Average per ticker: {total_time / (successful_count + failed_count):.1f} seconds")

    if failed_tickers:
        print(f"\n❌ Failed tickers ({len(failed_tickers)}):")
        for ticker in failed_tickers:
            print(f"  - {ticker}")

        # Save failed tickers for retry
        with open('data/failed_tickers.txt', 'w') as f:
            f.write('\n'.join(failed_tickers))
        print(f"\n📝 Failed tickers saved to data/failed_tickers.txt")

    print(f"\n✅ Progress saved to {progress_file}")
    print("=" * 80)

    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
