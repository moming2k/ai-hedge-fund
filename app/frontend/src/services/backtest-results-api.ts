/**
 * API client for backtest results endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface BacktestRunSummary {
  id: number;
  name: string | null;
  description: string | null;
  status: "IDLE" | "IN_PROGRESS" | "COMPLETE" | "ERROR";
  tickers: string[];
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_portfolio_value: number | null;
  total_return_pct: number | null;
  sharpe_ratio: number | null;
  sortino_ratio: number | null;
  max_drawdown: number | null;
  max_drawdown_date: string | null;
  long_short_ratio: number | null;
  gross_exposure: number | null;
  net_exposure: number | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

export interface BacktestDailyResult {
  id: number;
  backtest_run_id: number;
  date: string;
  portfolio_value: number;
  cash: number;
  decisions: Record<string, any> | null;
  executed_trades: Record<string, any> | null;
  analyst_signals: Record<string, any> | null;
  current_prices: Record<string, number> | null;
  long_exposure: number | null;
  short_exposure: number | null;
  gross_exposure: number | null;
  net_exposure: number | null;
  long_short_ratio: number | null;
  portfolio_return_pct: number | null;
  created_at: string;
}

export interface BacktestRunDetail extends BacktestRunSummary {
  graph_config: any | null;
  agent_models: any[] | null;
  request_data: any | null;
  final_portfolio: any | null;
  daily_results: BacktestDailyResult[] | null;
}

export interface BacktestRunsListResponse {
  total: number;
  skip: number;
  limit: number;
  runs: BacktestRunSummary[];
}

export class BacktestResultsApi {
  /**
   * Get a paginated list of backtest runs with optional filtering
   */
  async listBacktestRuns(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    ticker?: string;
  }): Promise<BacktestRunsListResponse> {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.set("skip", params.skip.toString());
    if (params?.limit !== undefined) queryParams.set("limit", params.limit.toString());
    if (params?.status) queryParams.set("status", params.status);
    if (params?.ticker) queryParams.set("ticker", params.ticker);

    const url = `${API_BASE_URL}/backtests?${queryParams.toString()}`;
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(`Failed to fetch backtest runs: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get detailed information about a specific backtest run
   */
  async getBacktestRun(
    backtestRunId: number,
    includeDailyResults: boolean = true
  ): Promise<BacktestRunDetail> {
    const url = `${API_BASE_URL}/backtests/${backtestRunId}?include_daily_results=${includeDailyResults}`;
    const response = await fetch(url);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`Backtest run ${backtestRunId} not found`);
      }
      throw new Error(`Failed to fetch backtest run: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get daily results for a specific backtest run with optional date filtering
   */
  async getDailyResults(
    backtestRunId: number,
    params?: {
      start_date?: string;
      end_date?: string;
    }
  ): Promise<BacktestDailyResult[]> {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.set("start_date", params.start_date);
    if (params?.end_date) queryParams.set("end_date", params.end_date);

    const url = `${API_BASE_URL}/backtests/${backtestRunId}/daily?${queryParams.toString()}`;
    const response = await fetch(url);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`Backtest run ${backtestRunId} not found`);
      }
      throw new Error(`Failed to fetch daily results: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete a backtest run and all its daily results
   */
  async deleteBacktestRun(backtestRunId: number): Promise<{ message: string }> {
    const url = `${API_BASE_URL}/backtests/${backtestRunId}`;
    const response = await fetch(url, {
      method: "DELETE",
    });

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`Backtest run ${backtestRunId} not found`);
      }
      throw new Error(`Failed to delete backtest run: ${response.statusText}`);
    }

    return response.json();
  }
}

// Export a singleton instance
export const backtestResultsApi = new BacktestResultsApi();
