#!/usr/bin/env python3
"""
Acquire historical data for all S&P 500 companies from 1999 to today
Processes companies one by one in order of market cap (largest first)
"""
import pandas as pd
import subprocess
import sys
from datetime import datetime
from pathlib import Path

print('S&P 500 Historical Data Acquisition')
print('=' * 80)

# Configuration
START_DATE = '1999-01-01'
END_DATE = datetime.now().strftime('%Y-%m-%d')
DATA_FILE = 'data/sp500.csv'

print(f'Date Range: {START_DATE} to {END_DATE}')
print(f'Source: {DATA_FILE}')
print()

# Load S&P 500 data (already sorted by market cap)
if not Path(DATA_FILE).exists():
    print(f'❌ Error: {DATA_FILE} not found!')
    print('Please run fetch_sp500_data.py first to generate the company list.')
    sys.exit(1)

df = pd.read_csv(DATA_FILE)
print(f'Loaded {len(df)} companies from {DATA_FILE}')
print()

# Create progress tracking file
progress_file = 'data/acquisition_progress.txt'
completed_tickers = set()

# Load previous progress if exists
if Path(progress_file).exists():
    with open(progress_file, 'r') as f:
        completed_tickers = set(line.strip() for line in f if line.strip())
    print(f'Resuming from previous run: {len(completed_tickers)} companies already completed')
    print()

# Filter out already completed tickers
remaining_df = df[~df['ticker'].isin(completed_tickers)]
print(f'Remaining companies to process: {len(remaining_df)}')
print()

if len(remaining_df) == 0:
    print('✅ All companies already processed!')
    sys.exit(0)

# Display top 10 companies to be processed
print('Top 10 companies to process:')
print('-' * 80)
for idx, row in remaining_df.head(10).iterrows():
    market_cap_t = row['market_cap'] / 1e12
    market_cap_b = row['market_cap'] / 1e9

    if market_cap_t >= 1:
        cap_str = f'${market_cap_t:.2f}T'
    else:
        cap_str = f'${market_cap_b:.1f}B'

    print(f"{row['ticker']:<8} {row['company_name'][:40]:<42} {cap_str}")

print('-' * 80)
print()

print()
print('=' * 80)
print('Starting data acquisition...')
print('=' * 80)
print()

# Process each company
success_count = 0
failure_count = 0
failed_tickers = []

for idx, (_, row) in enumerate(remaining_df.iterrows(), 1):
    ticker = row['ticker']
    company_name = row['company_name']

    print(f"[{idx}/{len(remaining_df)}] Processing {ticker} - {company_name[:50]}")

    try:
        # Run acquire_data command
        cmd = [
            'poetry', 'run', 'python', '-m', 'src.acquire_data',
            '--tickers', ticker,
            '--start-date', START_DATE,
            '--end-date', END_DATE,
            '--yes'  # Skip confirmation prompt
        ]

        # Set environment variables
        import os
        env = os.environ.copy()
        env['USE_YAHOO_FINANCE'] = 'true'
        env['POSTGRES_HOST'] = '127.0.0.1'
        env['POSTGRES_PORT'] = '5432'
        env['POSTGRES_DB'] = 'ai_hedge_fund'
        env['POSTGRES_USER'] = 'postgres'
        env['POSTGRES_PASSWORD'] = 'postgres'

        # Run command
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=3000  # 50 minute timeout per ticker
        )

        if result.returncode == 0:
            print(f"  ✅ Success: {ticker}")
            success_count += 1

            # Save progress
            with open(progress_file, 'a') as f:
                f.write(f'{ticker}\n')
        else:
            print(f"  ❌ Failed: {ticker}")
            print(f"  Error: {result.stderr[:200]}")
            failure_count += 1
            failed_tickers.append(ticker)

    except subprocess.TimeoutExpired:
        print(f"  ⏱️  Timeout: {ticker} (skipping)")
        failure_count += 1
        failed_tickers.append(ticker)

    except Exception as e:
        print(f"  ❌ Error: {ticker} - {str(e)[:100]}")
        failure_count += 1
        failed_tickers.append(ticker)

    print()

    # Progress summary every 10 companies
    if idx % 10 == 0:
        print('-' * 80)
        print(f'Progress: {idx}/{len(remaining_df)} companies processed')
        print(f'Success: {success_count} | Failed: {failure_count}')
        print('-' * 80)
        print()

# Final summary
print()
print('=' * 80)
print('Data Acquisition Complete!')
print('=' * 80)
print(f'Total companies processed: {len(remaining_df)}')
print(f'Successful: {success_count}')
print(f'Failed: {failure_count}')
print()

if failed_tickers:
    print('Failed tickers:')
    for ticker in failed_tickers[:20]:  # Show first 20
        print(f'  - {ticker}')
    if len(failed_tickers) > 20:
        print(f'  ... and {len(failed_tickers) - 20} more')
    print()

    # Save failed tickers to file
    failed_file = 'data/failed_tickers.txt'
    with open(failed_file, 'w') as f:
        for ticker in failed_tickers:
            f.write(f'{ticker}\n')
    print(f'Failed tickers saved to: {failed_file}')
    print()

print(f'Progress tracking file: {progress_file}')
print()
print('You can now run backtests with:')
print(f'  USE_DATABASE=true poetry run python -m src.backtester --tickers <TICKER> --start-date {START_DATE} --end-date {END_DATE}')
