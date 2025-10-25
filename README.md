# AI Hedge Fund

This is a proof of concept for an AI-powered hedge fund.  The goal of this project is to explore the use of AI to make trading decisions.  This project is for **educational** purposes only and is not intended for real trading or investment.

This system employs several agents working together:

1. Aswath Damodaran Agent - The Dean of Valuation, focuses on story, numbers, and disciplined valuation
2. Ben Graham Agent - The godfather of value investing, only buys hidden gems with a margin of safety
3. Bill Ackman Agent - An activist investor, takes bold positions and pushes for change
4. Cathie Wood Agent - The queen of growth investing, believes in the power of innovation and disruption
5. Charlie Munger Agent - Warren Buffett's partner, only buys wonderful businesses at fair prices
6. Michael Burry Agent - The Big Short contrarian who hunts for deep value
7. Mohnish Pabrai Agent - The Dhandho investor, who looks for doubles at low risk
8. Peter Lynch Agent - Practical investor who seeks "ten-baggers" in everyday businesses
9. Phil Fisher Agent - Meticulous growth investor who uses deep "scuttlebutt" research 
10. Rakesh Jhunjhunwala Agent - The Big Bull of India
11. Stanley Druckenmiller Agent - Macro legend who hunts for asymmetric opportunities with growth potential
12. Warren Buffett Agent - The oracle of Omaha, seeks wonderful companies at a fair price
13. Valuation Agent - Calculates the intrinsic value of a stock and generates trading signals
14. Sentiment Agent - Analyzes market sentiment and generates trading signals
15. Fundamentals Agent - Analyzes fundamental data and generates trading signals
16. Technicals Agent - Analyzes technical indicators and generates trading signals
17. Risk Manager - Calculates risk metrics and sets position limits
18. Portfolio Manager - Makes final trading decisions and generates orders

<img width="1042" alt="Screenshot 2025-03-22 at 6 19 07 PM" src="https://github.com/user-attachments/assets/cbae3dcf-b571-490d-b0ad-3f0f035ac0d4" />

Note: the system does not actually make any trades.

[![Twitter Follow](https://img.shields.io/twitter/follow/virattt?style=social)](https://twitter.com/virattt)

## Disclaimer

This project is for **educational and research purposes only**.

- Not intended for real trading or investment
- No investment advice or guarantees provided
- Creator assumes no liability for financial losses
- Consult a financial advisor for investment decisions
- Past performance does not indicate future results

By using this software, you agree to use it solely for learning purposes.

## Table of Contents
- [How to Install](#how-to-install)
- [How to Run](#how-to-run)
  - [⌨️ Command Line Interface](#️-command-line-interface)
    - [📊 Data Management: Two-Step Workflow](#-data-management-two-step-workflow-recommended-for-backtesting)
  - [🖥️ Web Application](#️-web-application)
- [Environment Variables Reference](#environment-variables-reference)
- [How to Contribute](#how-to-contribute)
- [Feature Requests](#feature-requests)
- [License](#license)

## How to Install

Before you can run the AI Hedge Fund, you'll need to install it and set up your API keys. These steps are common to both the full-stack web application and command line interface.

### 1. Clone the Repository

```bash
git clone https://github.com/virattt/ai-hedge-fund.git
cd ai-hedge-fund
```

### 2. Set up API keys

Create a `.env` file for your API keys:
```bash
# Create .env file for your API keys (in the root directory)
cp .env.example .env
```

Open and edit the `.env` file to add your API keys:
```bash
# For running LLMs hosted by openai (gpt-4o, gpt-4o-mini, etc.)
OPENAI_API_KEY=your-openai-api-key

# For getting financial data to power the hedge fund
FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key
```

**Important**: You must set at least one LLM API key (e.g. `OPENAI_API_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`, or `DEEPSEEK_API_KEY`) for the hedge fund to work.

**Financial Data Options**:
- **Yahoo Finance (Free)**: Set `USE_YAHOO_FINANCE=true` to use free Yahoo Finance data for any ticker
- **Financial Datasets API (Paid)**: Use `FINANCIAL_DATASETS_API_KEY` for comprehensive data including insider trades and sentiment
- **Database Cache (Recommended for Backtesting)**: Set `USE_DATABASE=true` to use pre-cached data for 10-20x faster backtests

Note: Data for AAPL, GOOGL, MSFT, NVDA, and TSLA is free with Financial Datasets API without a key.

## How to Run

### ⌨️ Command Line Interface

You can run the AI Hedge Fund directly via terminal. This approach offers more granular control and is useful for automation, scripting, and integration purposes.

<img width="992" alt="Screenshot 2025-01-06 at 5 50 17 PM" src="https://github.com/user-attachments/assets/e8ca04bf-9989-4a7d-a8b4-34e04666663b" />

#### Quick Start

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Set up PostgreSQL:

The system uses PostgreSQL for data caching. Choose one option:

**Option A: Docker (Recommended for Development)**
```bash
docker run --name ai-hedge-fund-postgres \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=ai_hedge_fund \
  -p 5432:5432 \
  -d postgres:16
```

**Option B: Local PostgreSQL**
```bash
# macOS
brew install postgresql@16
brew services start postgresql@16
createdb ai_hedge_fund

# Ubuntu/Debian
sudo apt update && sudo apt install postgresql
sudo systemctl start postgresql
sudo -u postgres createdb ai_hedge_fund
```

4. Configure database environment variables:

Add to your `.env` file:
```bash
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_hedge_fund
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
```

5. Initialize database tables:
```bash
export POSTGRES_PASSWORD=your_password
cd app/backend
python -c "from database.init_db import init_db; init_db()"
cd ../..
```

#### 📊 Data Management: Two-Step Workflow (Recommended for Backtesting)

For optimal performance, especially when running multiple backtests, we recommend using the **two-step data workflow** that separates data acquisition from analysis:

**Benefits:**
- ⚡ **10-20x faster backtests** - No API calls during analysis
- 💰 **Reduced API costs** - Fetch data once, reuse indefinitely
- 🔌 **Offline capability** - Run backtests without internet connection
- 📊 **Consistent data** - All backtests use the same historical snapshot
- 🔄 **Better iteration** - Quickly test different strategies

**Step 1: Acquire and Cache Data (One-time)**

```bash
# Using Yahoo Finance (free) - recommended for most users
poetry run python -m src.acquire_data \
  --tickers AAPL MSFT NVDA GOOGL \
  --start-date 2020-01-01 \
  --end-date 2024-12-31

# With environment variable
USE_YAHOO_FINANCE=true poetry run python -m src.acquire_data \
  --tickers AAPL MSFT NVDA \
  --start-date 2023-01-01 \
  --end-date 2023-12-31
```

Available options:
- `--tickers`: Space-separated list of ticker symbols (required)
- `--start-date`: Start date in YYYY-MM-DD format (required)
- `--end-date`: End date in YYYY-MM-DD format (defaults to today)
- `--force-refresh`: Re-fetch and update existing data
- `--prices-only`: Only acquire price data (skip metrics, news, etc.)

**Step 2: Run Analysis with Cached Data (Fast & Repeatable)**

```bash
# Run backtest using cached data - 10-20x faster!
USE_DATABASE=true poetry run python src/backtester.py \
  --ticker AAPL,MSFT,NVDA \
  --start-date 2023-01-01 \
  --end-date 2023-12-31
```

For detailed documentation on data caching, see [docs/DATA_CACHING.md](docs/DATA_CACHING.md).

#### Run the AI Hedge Fund
```bash
poetry run python src/main.py --ticker AAPL,MSFT,NVDA
```

You can also specify a `--ollama` flag to run the AI hedge fund using local LLMs.

```bash
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --ollama
```

You can optionally specify the start and end dates to make decisions over a specific time period.

```bash
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01
```

#### Run the Backtester

**Standard Mode (with real-time API calls):**
```bash
poetry run python src/backtester.py --ticker AAPL,MSFT,NVDA
```

**High-Performance Mode (with cached data - recommended):**
```bash
# First, acquire data (one-time)
USE_YAHOO_FINANCE=true poetry run python -m src.acquire_data \
  --tickers AAPL MSFT NVDA \
  --start-date 2023-01-01 \
  --end-date 2023-12-31

# Then run backtest with cached data (10-20x faster!)
USE_DATABASE=true poetry run python src/backtester.py \
  --ticker AAPL,MSFT,NVDA \
  --start-date 2023-01-01 \
  --end-date 2023-12-31
```

**Example Output:**
<img width="941" alt="Screenshot 2025-01-06 at 5 47 52 PM" src="https://github.com/user-attachments/assets/00e794ea-8628-44e6-9a84-8f8a31ad3b47" />


Note: The `--ollama`, `--start-date`, and `--end-date` flags work for the backtester, as well!

💡 **Pro Tip**: For repeated backtests with different parameters, use the two-step workflow (acquire data once, then run multiple backtests with `USE_DATABASE=true`) for significant time savings.

### 🖥️ Web Application

The new way to run the AI Hedge Fund is through our web application that provides a user-friendly interface. This is recommended for users who prefer visual interfaces over command line tools.

Please see detailed instructions on how to install and run the web application [here](https://github.com/virattt/ai-hedge-fund/tree/main/app).

<img width="1721" alt="Screenshot 2025-06-28 at 6 41 03 PM" src="https://github.com/user-attachments/assets/b95ab696-c9f4-416c-9ad1-51feb1f5374b" />


## Environment Variables Reference

The AI Hedge Fund supports several environment variables to configure data sources and behavior:

### Data Source Selection

| Variable | Values | Description |
|----------|--------|-------------|
| `USE_DATABASE` | `true`/`false` | Use cached database data (recommended for backtesting) |
| `USE_YAHOO_FINANCE` | `true`/`false` | Use Yahoo Finance API (free, real-time data) |
| (none) | - | Use Financial Datasets API (paid, requires API key) |

**Priority**: `USE_DATABASE` > `USE_YAHOO_FINANCE` > Financial Datasets API

### Example Workflows

**For Data Acquisition:**
```bash
# Use Yahoo Finance to fetch and cache data
USE_YAHOO_FINANCE=true poetry run python -m src.acquire_data --tickers AAPL --start-date 2023-01-01
```

**For Backtesting:**
```bash
# Use cached data for fast backtests
USE_DATABASE=true poetry run python src/backtester.py --ticker AAPL --start-date 2023-01-01
```

**For Real-time Analysis:**
```bash
# Use Yahoo Finance for real-time data
USE_YAHOO_FINANCE=true poetry run python src/main.py --ticker AAPL
```

### Performance Comparison

| Mode | Speed | Cost | Use Case |
|------|-------|------|----------|
| Database Cache (`USE_DATABASE=true`) | ⚡⚡⚡ Fastest (10-20x) | Free | Backtesting, strategy iteration |
| Yahoo Finance (`USE_YAHOO_FINANCE=true`) | ⚡⚡ Fast | Free | Real-time analysis, data acquisition |
| Financial Datasets API | ⚡ Standard | Paid | Comprehensive data needs |

## How to Contribute

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

**Important**: Please keep your pull requests small and focused.  This will make it easier to review and merge.

## Feature Requests

If you have a feature request, please open an [issue](https://github.com/virattt/ai-hedge-fund/issues) and make sure it is tagged with `enhancement`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
