# Data Caching and Two-Step Backtesting

This document explains how to use the two-step backtesting workflow that separates data acquisition from analysis, significantly improving performance for repeated backtests.

## Overview

The AI Hedge Fund now supports a **two-step workflow**:

1. **Step 1: Data Acquisition** - Fetch data from external APIs (Yahoo Finance or Financial Datasets) and cache it in a PostgreSQL database
2. **Step 2: Analysis** - Run backtests using the cached data from the database (no API calls)

### Benefits

- **Faster backtests**: No need to wait for API calls on subsequent runs
- **Reduced API costs**: Only fetch data once, reuse it indefinitely
- **Offline analysis**: Run backtests without internet connection after initial data acquisition
- **Consistent data**: All backtests use the same historical data snapshot
- **Better testing**: Quickly iterate on trading strategies without re-fetching data
- **Scalability**: PostgreSQL handles large datasets efficiently
- **Multi-user support**: Multiple users can access cached data simultaneously

## Prerequisites

### PostgreSQL Setup

Before using the data caching system, you need to have PostgreSQL installed and running.

#### Option 1: Local PostgreSQL Installation

**macOS (using Homebrew):**
```bash
brew install postgresql@16
brew services start postgresql@16
createdb ai_hedge_fund
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb ai_hedge_fund
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_password';"
```

**Windows:**
Download and install from [PostgreSQL official site](https://www.postgresql.org/download/windows/)

#### Option 2: Docker (Recommended for Development)

```bash
# Start PostgreSQL in Docker
docker run --name ai-hedge-fund-postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=ai_hedge_fund \
  -p 5432:5432 \
  -d postgres:16

# Verify it's running
docker ps
```

#### Option 3: Cloud Managed PostgreSQL

Use managed PostgreSQL services like:
- AWS RDS
- Google Cloud SQL
- Azure Database for PostgreSQL
- DigitalOcean Managed Databases
- Heroku Postgres
- Supabase

### Environment Variables

Set the following environment variables for PostgreSQL connection:

```bash
# Option 1: Full DATABASE_URL (recommended for production)
export DATABASE_URL="postgresql://user:password@host:port/database"

# Option 2: Individual components (recommended for development)
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=ai_hedge_fund
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_password
```

Add these to your `.env` file:
```bash
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_hedge_fund
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

## Architecture

### Data Sources

The system supports three data sources, controlled by environment variables:

| Environment Variable | Data Source | Use Case |
|---------------------|-------------|----------|
| `USE_DATABASE=true` | PostgreSQL Database | Fast backtesting with cached data |
| `USE_YAHOO_FINANCE=true` | Yahoo Finance API | Free, real-time data acquisition |
| (none set) | Financial Datasets API | Paid, comprehensive data |

### Database Schema

Market data is stored in four tables:

1. **historical_prices** - OHLCV price data
2. **financial_metrics** - Valuation ratios, profitability, growth metrics
3. **company_news** - News articles with sentiment
4. **insider_trades** - Insider trading activity

## Usage

### Step 1: Acquire Data

Use the `acquire_data` CLI to fetch and cache market data:

```bash
# Basic usage - acquire 1 year of data for AAPL
python -m src.acquire_data \
  --tickers AAPL \
  --start-date 2023-01-01 \
  --end-date 2023-12-31

# Multiple tickers
python -m src.acquire_data \
  --tickers AAPL MSFT GOOGL AMZN \
  --start-date 2020-01-01 \
  --end-date 2024-12-31

# Use Yahoo Finance (free) as data source
USE_YAHOO_FINANCE=true python -m src.acquire_data \
  --tickers AAPL MSFT \
  --start-date 2023-01-01 \
  --end-date 2023-12-31

# Force refresh existing data
python -m src.acquire_data \
  --tickers AAPL \
  --start-date 2023-01-01 \
  --end-date 2023-12-31 \
  --force-refresh

# Acquire only price data (skip metrics, news, insider trades)
python -m src.acquire_data \
  --tickers AAPL \
  --start-date 2023-01-01 \
  --end-date 2023-12-31 \
  --prices-only
```

#### Options

- `--tickers`: Space-separated list of ticker symbols (required)
- `--start-date`: Start date in YYYY-MM-DD format (required)
- `--end-date`: End date in YYYY-MM-DD format (defaults to today)
- `--force-refresh`: Re-fetch and update existing data
- `--prices-only`: Only acquire price data
- `--no-prices`: Skip price data acquisition
- `--no-metrics`: Skip financial metrics
- `--no-news`: Skip company news
- `--no-insider-trades`: Skip insider trades

### Step 2: Run Backtests

Once data is acquired, run backtests with `USE_DATABASE=true`:

```bash
# Run backtest using cached database data
USE_DATABASE=true python -m src.backtester \
  --tickers AAPL MSFT \
  --start-date 2023-01-01 \
  --end-date 2023-12-31 \
  --agents buffett \
  --show-reasoning

# Using the new backtesting CLI
USE_DATABASE=true python -m src.backtesting.cli \
  --tickers AAPL MSFT GOOGL \
  --start-date 2023-01-01 \
  --end-date 2023-12-31 \
  --agents buffett graham \
  --model gpt-4o \
  --show-reasoning
```

## Complete Workflow Example

Here's a complete example workflow:

```bash
# 1. Acquire data using Yahoo Finance (free)
echo "Step 1: Acquiring market data..."
USE_YAHOO_FINANCE=true python -m src.acquire_data \
  --tickers AAPL MSFT GOOGL AMZN NVDA \
  --start-date 2020-01-01 \
  --end-date 2024-12-31

# 2. Run backtest using cached data
echo "Step 2: Running backtest..."
USE_DATABASE=true python -m src.backtesting.cli \
  --tickers AAPL MSFT GOOGL AMZN NVDA \
  --start-date 2023-01-01 \
  --end-date 2023-12-31 \
  --agents buffett graham \
  --model gpt-4o \
  --show-reasoning

# 3. Run another backtest with different parameters (reuses cached data)
echo "Step 3: Running backtest with different date range..."
USE_DATABASE=true python -m src.backtesting.cli \
  --tickers AAPL MSFT GOOGL \
  --start-date 2022-01-01 \
  --end-date 2022-12-31 \
  --agents buffett \
  --model claude-3-5-sonnet-20241022
```

## Database Management

### Connecting to PostgreSQL

You can inspect the database using `psql` or any PostgreSQL client:

```bash
# Connect using psql
psql -h localhost -U postgres -d ai_hedge_fund

# Or if using DATABASE_URL
psql $DATABASE_URL

# View available tables
\dt

# Query price data
SELECT ticker, date, close FROM historical_prices WHERE ticker = 'AAPL' LIMIT 10;

# Check data coverage
SELECT ticker, COUNT(*) as days, MIN(date) as start_date, MAX(date) as end_date
FROM historical_prices
GROUP BY ticker;

# Check database size
SELECT pg_size_pretty(pg_database_size('ai_hedge_fund'));

# Exit psql
\q
```

### Using GUI Tools

Popular PostgreSQL GUI tools:
- **pgAdmin**: Official PostgreSQL administration tool
- **DBeaver**: Universal database tool
- **TablePlus**: Modern database GUI (macOS/Windows)
- **DataGrip**: JetBrains database IDE
- **Postico**: PostgreSQL client for macOS

### Database Initialization

Create the database tables using Alembic migrations:

```bash
# Set environment variables first
export POSTGRES_PASSWORD=your_password

# Navigate to backend directory
cd app/backend

# Run migrations to create tables
python -c "from database.init_db import init_db; init_db()"
```

Or manually create tables:
```bash
# Using psql
psql -h localhost -U postgres -d ai_hedge_fund -c "CREATE TABLE IF NOT EXISTS ..."
```

## Performance Comparison

### Without Data Caching (Traditional)
```bash
# Each backtest makes fresh API calls
time python -m src.backtester --tickers AAPL MSFT --start-date 2023-01-01 --end-date 2023-12-31
# Result: ~60-120 seconds (depending on network and API rate limits)
```

### With Data Caching (Two-Step)
```bash
# Step 1: Acquire data once
time python -m src.acquire_data --tickers AAPL MSFT --start-date 2023-01-01 --end-date 2023-12-31
# Result: ~60-120 seconds (first time only)

# Step 2: Run backtest (reuses cached data)
time USE_DATABASE=true python -m src.backtester --tickers AAPL MSFT --start-date 2023-01-01 --end-date 2023-12-31
# Result: ~5-15 seconds (10-20x faster!)

# Step 3: Run another backtest (reuses cached data)
time USE_DATABASE=true python -m src.backtester --tickers AAPL MSFT --start-date 2023-01-01 --end-date 2023-12-31
# Result: ~5-15 seconds (no API calls!)
```

## Data Freshness

### Updating Data

To update your cached data with new information:

```bash
# Update all data for specific tickers
python -m src.acquire_data \
  --tickers AAPL MSFT \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --force-refresh
```

The `--force-refresh` flag will update existing records and add new ones.

### Partial Updates

You can acquire data for new date ranges without re-fetching existing data:

```bash
# Already have 2020-2023 data, add 2024 data
python -m src.acquire_data \
  --tickers AAPL \
  --start-date 2024-01-01 \
  --end-date 2024-12-31
# This will skip existing data and only fetch new records
```

## Best Practices

1. **Acquire data once, backtest many times**: Run data acquisition once for a long period (e.g., 5 years), then experiment with different backtesting parameters

2. **Use Yahoo Finance for acquisition**: It's free and suitable for most use cases
   ```bash
   USE_YAHOO_FINANCE=true python -m src.acquire_data --tickers AAPL --start-date 2020-01-01
   ```

3. **Acquire more data than you need**: Fetch extra years of data upfront to support various backtesting scenarios
   ```bash
   # Acquire 10 years of data
   python -m src.acquire_data --tickers AAPL --start-date 2014-01-01 --end-date 2024-12-31
   ```

4. **Check data coverage before backtesting**: Ensure you have data for your desired date range
   ```bash
   psql -h localhost -U postgres -d ai_hedge_fund -c "SELECT ticker, MIN(date), MAX(date), COUNT(*) FROM historical_prices GROUP BY ticker;"
   ```

5. **Periodic updates**: Schedule weekly or monthly data updates to keep your cache fresh
   ```bash
   # Add to cron or scheduler
   USE_YAHOO_FINANCE=true python -m src.acquire_data --tickers AAPL MSFT --end-date $(date +%Y-%m-%d) --force-refresh
   ```

## Troubleshooting

### "PostgreSQL password is required" Error

Set the `POSTGRES_PASSWORD` environment variable:
```bash
export POSTGRES_PASSWORD=your_password

# Or add to .env file
echo "POSTGRES_PASSWORD=your_password" >> .env
```

### "Connection to database failed" Error

Ensure PostgreSQL is running:
```bash
# macOS (Homebrew)
brew services status postgresql@16

# Linux
sudo systemctl status postgresql

# Docker
docker ps | grep postgres
```

If not running, start it:
```bash
# macOS
brew services start postgresql@16

# Linux
sudo systemctl start postgresql

# Docker
docker start ai-hedge-fund-postgres
```

### "Database does not exist" Error

Create the database:
```bash
# Using createdb command
createdb ai_hedge_fund

# Or using psql
psql -U postgres -c "CREATE DATABASE ai_hedge_fund;"

# Docker
docker exec -it ai-hedge-fund-postgres createdb -U postgres ai_hedge_fund
```

### "No price data found in database" Warning

You need to acquire data first:
```bash
python -m src.acquire_data --tickers AAPL --start-date 2023-01-01 --end-date 2023-12-31
```

### "psycopg2" Module Not Found

Install PostgreSQL dependencies:
```bash
poetry install
# Or
pip install psycopg2-binary
```

### Resetting the Database

To start fresh, drop and recreate the database:
```bash
# Drop database
dropdb ai_hedge_fund

# Recreate database
createdb ai_hedge_fund

# Or using psql
psql -U postgres -c "DROP DATABASE IF EXISTS ai_hedge_fund;"
psql -U postgres -c "CREATE DATABASE ai_hedge_fund;"

# Re-run initialization
cd app/backend
python -c "from database.init_db import init_db; init_db()"
```

Then re-run the data acquisition.

### Connection Pool Errors

If you see "connection pool exhausted" errors, adjust the pool settings in `app/backend/database/connection.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,  # Increase pool size
    max_overflow=40,  # Increase max overflow
)

## API Reference

### Data Acquisition Module

Located at `src/data/acquisition.py`:

```python
from src.data.acquisition import acquire_all_data

# Acquire data programmatically
results = acquire_all_data(
    tickers=['AAPL', 'MSFT'],
    start_date='2023-01-01',
    end_date='2023-12-31',
    include_prices=True,
    include_metrics=True,
    include_news=True,
    include_insider_trades=True,
    force_refresh=False
)
```

### Database API

Located at `src/tools/api_database.py`:

```python
from src.tools.api_database import get_prices, get_financial_metrics

# Load from database (same interface as API)
prices = get_prices('AAPL', '2023-01-01', '2023-12-31')
metrics = get_financial_metrics('AAPL', '2023-12-31')
```

## Migration Guide

### Existing Workflows

No changes needed! The system is backward compatible:

```bash
# This still works (uses API directly)
python -m src.backtester --tickers AAPL --start-date 2023-01-01 --end-date 2023-12-31

# This uses cached data (faster)
USE_DATABASE=true python -m src.backtester --tickers AAPL --start-date 2023-01-01 --end-date 2023-12-31
```

### Recommended Migration Path

1. Run data acquisition for all your historical needs
2. Switch to `USE_DATABASE=true` for all backtesting
3. Periodically update the database with new data
4. Continue using API mode for real-time analysis if needed

## Future Enhancements

Potential improvements to the data caching system:

- [ ] Automatic data refresh scheduling
- [ ] Data validation and quality checks
- [ ] Compression for large datasets
- [ ] Incremental updates without full refresh
- [ ] Multi-database support (PostgreSQL, MySQL)
- [ ] Data versioning and snapshots
- [ ] Web UI for data management

## Summary

The two-step workflow separates concerns:

1. **Data acquisition** (slow, one-time) → Uses external APIs to populate database
2. **Analysis** (fast, repeatable) → Uses cached database data for backtesting

This architecture provides:
- ✅ Faster backtests (10-20x speedup)
- ✅ Lower API costs
- ✅ Offline capability
- ✅ Consistent data across runs
- ✅ Better iteration speed for strategy development

Happy backtesting! 🚀
