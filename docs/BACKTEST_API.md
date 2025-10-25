# Backtest Results API Documentation

This document describes the new API endpoints for persisting and viewing backtest results.

## Overview

The backtest persistence system automatically saves all backtest runs and their daily results to a PostgreSQL database. This allows you to:
- View historical backtest results
- Compare different backtest runs
- Analyze performance over time
- Build UI dashboards to visualize results

## Database Schema

### Backtest Runs Table
Stores metadata and summary metrics for each backtest execution:
- Run metadata (name, description, status, timestamps)
- Backtest parameters (tickers, date range, initial capital)
- Performance metrics (Sharpe ratio, Sortino ratio, max drawdown, etc.)
- Configuration (graph structure, agent models)
- Final portfolio state

### Backtest Daily Results Table
Stores detailed daily results for each backtest run:
- Daily portfolio values and cash
- Trading decisions and executed trades
- Analyst signals from all agents
- Current prices for all tickers
- Exposure metrics (long, short, gross, net)
- Daily return percentage

## API Endpoints

### 1. List All Backtest Runs

**Endpoint:** `GET /backtests`

**Description:** Get a paginated list of all backtest runs with optional filtering.

**Query Parameters:**
- `skip` (int, default: 0): Number of records to skip (for pagination)
- `limit` (int, default: 100, max: 1000): Maximum number of records to return
- `status` (string, optional): Filter by status (IDLE, IN_PROGRESS, COMPLETE, ERROR)
- `ticker` (string, optional): Filter by ticker symbol

**Example Request:**
```bash
curl -X GET "http://localhost:8000/backtests?limit=10&status=COMPLETE"
```

**Example Response:**
```json
{
  "total": 42,
  "skip": 0,
  "limit": 10,
  "runs": [
    {
      "id": 1,
      "name": "AAPL Long-Short Strategy",
      "description": "Testing long-short strategy on Apple stock",
      "status": "COMPLETE",
      "tickers": ["AAPL"],
      "start_date": "2023-01-01",
      "end_date": "2023-12-31",
      "initial_capital": 100000.0,
      "final_portfolio_value": 125000.0,
      "total_return_pct": 25.0,
      "sharpe_ratio": 1.5,
      "sortino_ratio": 2.1,
      "max_drawdown": -5.2,
      "max_drawdown_date": "2023-08-15",
      "long_short_ratio": 1.2,
      "gross_exposure": 150000.0,
      "net_exposure": 25000.0,
      "created_at": "2024-01-15T10:30:00Z",
      "started_at": "2024-01-15T10:30:05Z",
      "completed_at": "2024-01-15T10:45:00Z",
      "error_message": null
    }
  ]
}
```

---

### 2. Get Backtest Run Details

**Endpoint:** `GET /backtests/{backtest_run_id}`

**Description:** Get detailed information about a specific backtest run, optionally including daily results.

**Path Parameters:**
- `backtest_run_id` (int): The ID of the backtest run

**Query Parameters:**
- `include_daily_results` (bool, default: true): Whether to include daily results

**Example Request:**
```bash
curl -X GET "http://localhost:8000/backtests/1?include_daily_results=true"
```

**Example Response:**
```json
{
  "id": 1,
  "name": "AAPL Long-Short Strategy",
  "description": "Testing long-short strategy on Apple stock",
  "status": "COMPLETE",
  "tickers": ["AAPL"],
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 100000.0,
  "final_portfolio_value": 125000.0,
  "total_return_pct": 25.0,
  "sharpe_ratio": 1.5,
  "sortino_ratio": 2.1,
  "max_drawdown": -5.2,
  "max_drawdown_date": "2023-08-15",
  "long_short_ratio": 1.2,
  "gross_exposure": 150000.0,
  "net_exposure": 25000.0,
  "graph_config": {
    "nodes": [...],
    "edges": [...]
  },
  "agent_models": [...],
  "request_data": {...},
  "final_portfolio": {
    "cash": 50000.0,
    "positions": {...}
  },
  "created_at": "2024-01-15T10:30:00Z",
  "started_at": "2024-01-15T10:30:05Z",
  "completed_at": "2024-01-15T10:45:00Z",
  "error_message": null,
  "daily_results": [
    {
      "id": 1,
      "backtest_run_id": 1,
      "date": "2023-01-03",
      "portfolio_value": 100500.0,
      "cash": 90000.0,
      "decisions": {
        "AAPL": {"action": "buy", "quantity": 100}
      },
      "executed_trades": {
        "AAPL": 100
      },
      "analyst_signals": {
        "valuation_agent": {...},
        "sentiment_agent": {...}
      },
      "current_prices": {
        "AAPL": 105.0
      },
      "long_exposure": 10500.0,
      "short_exposure": 0.0,
      "gross_exposure": 10500.0,
      "net_exposure": 10500.0,
      "long_short_ratio": null,
      "portfolio_return_pct": 0.5,
      "created_at": "2024-01-15T10:30:10Z"
    }
  ]
}
```

---

### 3. Get Daily Results for a Backtest Run

**Endpoint:** `GET /backtests/{backtest_run_id}/daily`

**Description:** Get daily results for a specific backtest run with optional date filtering.

**Path Parameters:**
- `backtest_run_id` (int): The ID of the backtest run

**Query Parameters:**
- `start_date` (string, optional): Filter from this date (YYYY-MM-DD)
- `end_date` (string, optional): Filter to this date (YYYY-MM-DD)

**Example Request:**
```bash
curl -X GET "http://localhost:8000/backtests/1/daily?start_date=2023-06-01&end_date=2023-06-30"
```

**Example Response:**
```json
[
  {
    "id": 100,
    "backtest_run_id": 1,
    "date": "2023-06-01",
    "portfolio_value": 110500.0,
    "cash": 85000.0,
    "decisions": {...},
    "executed_trades": {...},
    "analyst_signals": {...},
    "current_prices": {...},
    "long_exposure": 15000.0,
    "short_exposure": 5000.0,
    "gross_exposure": 20000.0,
    "net_exposure": 10000.0,
    "long_short_ratio": 3.0,
    "portfolio_return_pct": 10.5,
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

---

### 4. Delete a Backtest Run

**Endpoint:** `DELETE /backtests/{backtest_run_id}`

**Description:** Delete a backtest run and all its daily results.

**Path Parameters:**
- `backtest_run_id` (int): The ID of the backtest run to delete

**Example Request:**
```bash
curl -X DELETE "http://localhost:8000/backtests/1"
```

**Example Response:**
```json
{
  "message": "Backtest run 1 deleted successfully"
}
```

---

## Automatic Persistence

When you run a backtest via the `/hedge-fund/backtest` endpoint, the results are **automatically persisted** to the database. You don't need to do anything special - just run your backtest as usual:

```bash
curl -X POST "http://localhost:8000/hedge-fund/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "initial_capital": 100000,
    "graph_nodes": [...],
    "graph_edges": [...]
  }'
```

The backtest will:
1. Create a `backtest_run` record with status "IN_PROGRESS"
2. Save each day's results to `backtest_daily_results` as the backtest progresses
3. Update the `backtest_run` with final metrics when complete

The backtest run ID is returned in the response so you can query it later:

```json
{
  "results": [...],
  "performance_metrics": {...},
  "final_portfolio": {...},
  "backtest_run_id": 123
}
```

## Use Cases

### Building a Dashboard

Fetch all completed backtest runs and display them in a table:

```javascript
const response = await fetch('/backtests?status=COMPLETE&limit=50');
const data = await response.json();

// Display data.runs in your UI
data.runs.forEach(run => {
  console.log(`${run.name}: ${run.total_return_pct}% return`);
});
```

### Comparing Strategies

Fetch multiple backtest runs and compare their performance:

```javascript
const run1 = await fetch('/backtests/1').then(r => r.json());
const run2 = await fetch('/backtests/2').then(r => r.json());

console.log('Strategy 1 Sharpe:', run1.sharpe_ratio);
console.log('Strategy 2 Sharpe:', run2.sharpe_ratio);
```

### Analyzing Daily Performance

Fetch daily results and create a performance chart:

```javascript
const daily = await fetch('/backtests/1/daily').then(r => r.json());

const chartData = daily.map(day => ({
  date: day.date,
  value: day.portfolio_value,
  return: day.portfolio_return_pct
}));

// Plot chartData in your charting library
```

### Filtering by Date Range

Get results for a specific time period:

```javascript
const june2023 = await fetch(
  '/backtests/1/daily?start_date=2023-06-01&end_date=2023-06-30'
).then(r => r.json());

console.log(`June 2023: ${june2023.length} trading days`);
```

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid parameters
- `404 Not Found`: Backtest run not found
- `500 Internal Server Error`: Server error

Error responses include a descriptive message:

```json
{
  "detail": "Backtest run 999 not found"
}
```

## Database Schema Details

### backtest_runs Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| created_at | DateTime | When the run was created |
| started_at | DateTime | When execution started |
| completed_at | DateTime | When execution completed |
| name | String(200) | Optional user-provided name |
| description | Text | Optional description |
| status | String(50) | IDLE, IN_PROGRESS, COMPLETE, ERROR |
| tickers | JSON | Array of ticker symbols |
| start_date | Date | Backtest start date |
| end_date | Date | Backtest end date |
| initial_capital | Float | Starting capital |
| final_portfolio_value | Float | Final portfolio value |
| total_return_pct | Float | Total return percentage |
| sharpe_ratio | Float | Sharpe ratio |
| sortino_ratio | Float | Sortino ratio |
| max_drawdown | Float | Maximum drawdown percentage |
| max_drawdown_date | Date | Date of maximum drawdown |
| long_short_ratio | Float | Long/short exposure ratio |
| gross_exposure | Float | Gross exposure |
| net_exposure | Float | Net exposure |
| graph_config | JSON | Graph configuration |
| agent_models | JSON | Agent model configurations |
| request_data | JSON | Full request parameters |
| final_portfolio | JSON | Final portfolio state |
| error_message | Text | Error details if failed |

### backtest_daily_results Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| backtest_run_id | Integer | Foreign key to backtest_runs |
| date | Date | Trading date |
| portfolio_value | Float | Portfolio value on this date |
| cash | Float | Cash balance |
| decisions | JSON | Trading decisions |
| executed_trades | JSON | Actual trades executed |
| analyst_signals | JSON | Agent signals/analysis |
| current_prices | JSON | Prices for all tickers |
| long_exposure | Float | Long exposure |
| short_exposure | Float | Short exposure |
| gross_exposure | Float | Gross exposure |
| net_exposure | Float | Net exposure |
| long_short_ratio | Float | Long/short ratio |
| portfolio_return_pct | Float | Cumulative return % |
| created_at | DateTime | When record was created |

## Performance Considerations

1. **Pagination**: Always use `skip` and `limit` parameters when listing backtest runs to avoid loading too much data.

2. **Daily Results**: When fetching backtest details, set `include_daily_results=false` if you only need the summary metrics.

3. **Date Filtering**: Use date range filters when querying daily results to reduce data transfer.

4. **Indexes**: The database has indexes on frequently queried columns:
   - `(status, created_at)` on backtest_runs
   - `(start_date, end_date)` on backtest_runs
   - `(backtest_run_id, date)` on backtest_daily_results

## Next Steps

With persistent backtest results, you can now:

1. **Build a UI Dashboard**: Create a React/Vue component to display backtest history
2. **Compare Strategies**: Run multiple backtests with different parameters and compare results
3. **Track Performance**: Monitor how your strategies perform over time
4. **Export Data**: Fetch results via API and export to Excel/CSV for further analysis
5. **Share Results**: Share backtest URLs with team members for collaboration

## Support

For issues or questions, please refer to the main project README or open an issue on GitHub.
