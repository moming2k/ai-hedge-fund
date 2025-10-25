import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowLeft, TrendingUp, TrendingDown, Calendar, DollarSign, Loader2, BarChart3 } from "lucide-react";
import { backtestResultsApi, BacktestRunDetail, BacktestDailyResult } from "@/services/backtest-results-api";
import { toast } from "sonner";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from "recharts";

interface BacktestDetailViewProps {
  backtestRunId: number;
  onBack: () => void;
}

export function BacktestDetailView({ backtestRunId, onBack }: BacktestDetailViewProps) {
  const [backtest, setBacktest] = useState<BacktestRunDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    loadBacktestDetails();
  }, [backtestRunId]);

  const loadBacktestDetails = async () => {
    setLoading(true);
    try {
      const data = await backtestResultsApi.getBacktestRun(backtestRunId, true);
      setBacktest(data);
    } catch (error) {
      console.error("Failed to load backtest details:", error);
      toast.error("Failed to load backtest details");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString();
  };

  const formatNumber = (num: number | null, decimals: number = 2) => {
    if (num === null || num === undefined) return "N/A";
    return num.toFixed(decimals);
  };

  const formatCurrency = (num: number | null) => {
    if (num === null || num === undefined) return "N/A";
    return `$${num.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; label: string }> = {
      COMPLETE: { variant: "default", label: "Complete" },
      IN_PROGRESS: { variant: "secondary", label: "Running" },
      ERROR: { variant: "destructive", label: "Error" },
      IDLE: { variant: "outline", label: "Idle" },
    };

    const config = variants[status] || variants.IDLE;
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!backtest) {
    return (
      <div className="text-center py-12">
        <p className="text-muted-foreground">Backtest not found</p>
        <Button onClick={onBack} className="mt-4">
          Go Back
        </Button>
      </div>
    );
  }

  // Prepare chart data
  const chartData = backtest.daily_results?.map(result => ({
    date: formatDate(result.date),
    value: result.portfolio_value,
    return: result.portfolio_return_pct,
    longExposure: result.long_exposure,
    shortExposure: result.short_exposure,
  })) || [];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={onBack}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h2 className="text-2xl font-bold">{backtest.name || `Backtest #${backtest.id}`}</h2>
            <p className="text-muted-foreground">{backtest.description || "No description"}</p>
          </div>
        </div>
        {getStatusBadge(backtest.status)}
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Return</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {backtest.total_return_pct !== null && backtest.total_return_pct > 0 ? (
                <TrendingUp className="w-5 h-5 text-green-600 dark:text-green-400" />
              ) : (
                <TrendingDown className="w-5 h-5 text-red-600 dark:text-red-400" />
              )}
              <div className={`text-2xl font-bold ${backtest.total_return_pct !== null && backtest.total_return_pct > 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
                {formatNumber(backtest.total_return_pct)}%
              </div>
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              {formatCurrency(backtest.final_portfolio_value)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Sharpe Ratio</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(backtest.sharpe_ratio)}</div>
            <p className="text-sm text-muted-foreground mt-1">Risk-adjusted return</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Max Drawdown</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {formatNumber(backtest.max_drawdown)}%
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              {formatDate(backtest.max_drawdown_date)}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Sortino Ratio</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(backtest.sortino_ratio)}</div>
            <p className="text-sm text-muted-foreground mt-1">Downside risk focus</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="trades">Daily Trades</TabsTrigger>
          <TabsTrigger value="config">Configuration</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Backtest Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Tickers</p>
                  <p className="font-medium">{backtest.tickers.join(", ")}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Initial Capital</p>
                  <p className="font-medium">{formatCurrency(backtest.initial_capital)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Start Date</p>
                  <p className="font-medium">{formatDate(backtest.start_date)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">End Date</p>
                  <p className="font-medium">{formatDate(backtest.end_date)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Trading Days</p>
                  <p className="font-medium">{backtest.daily_results?.length || 0}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Long/Short Ratio</p>
                  <p className="font-medium">{formatNumber(backtest.long_short_ratio)}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Exposure Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Gross Exposure</p>
                  <p className="font-medium">{formatCurrency(backtest.gross_exposure)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Net Exposure</p>
                  <p className="font-medium">{formatCurrency(backtest.net_exposure)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Value Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                    name="Portfolio Value"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Cumulative Return %</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="return"
                    stroke="#82ca9d"
                    strokeWidth={2}
                    name="Return %"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Long/Short Exposure</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Area
                    type="monotone"
                    dataKey="longExposure"
                    stackId="1"
                    stroke="#82ca9d"
                    fill="#82ca9d"
                    name="Long Exposure"
                  />
                  <Area
                    type="monotone"
                    dataKey="shortExposure"
                    stackId="1"
                    stroke="#ff6b6b"
                    fill="#ff6b6b"
                    name="Short Exposure"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Trades Tab */}
        <TabsContent value="trades" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Daily Trading Activity</CardTitle>
              <CardDescription>
                {backtest.daily_results?.length || 0} trading days
              </CardDescription>
            </CardHeader>
            <CardContent>
              {backtest.daily_results && backtest.daily_results.length > 0 ? (
                <div className="border rounded-lg max-h-96 overflow-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead className="text-right">Portfolio Value</TableHead>
                        <TableHead className="text-right">Cash</TableHead>
                        <TableHead className="text-right">Return %</TableHead>
                        <TableHead>Trades</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {backtest.daily_results.map((result) => {
                        const hasTrades = result.executed_trades && Object.keys(result.executed_trades).length > 0;
                        const tradesStr = hasTrades
                          ? Object.entries(result.executed_trades || {})
                              .filter(([_, qty]) => qty !== 0)
                              .map(([ticker, qty]) => `${ticker}: ${qty}`)
                              .join(", ")
                          : "No trades";

                        return (
                          <TableRow key={result.id}>
                            <TableCell className="font-medium">
                              {formatDate(result.date)}
                            </TableCell>
                            <TableCell className="text-right">
                              {formatCurrency(result.portfolio_value)}
                            </TableCell>
                            <TableCell className="text-right">
                              {formatCurrency(result.cash)}
                            </TableCell>
                            <TableCell className={`text-right font-medium ${result.portfolio_return_pct && result.portfolio_return_pct > 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
                              {formatNumber(result.portfolio_return_pct)}%
                            </TableCell>
                            <TableCell className="text-sm text-muted-foreground">
                              {tradesStr}
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </div>
              ) : (
                <p className="text-center text-muted-foreground py-8">No daily results available</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Configuration Tab */}
        <TabsContent value="config" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Graph Configuration</CardTitle>
            </CardHeader>
            <CardContent>
              {backtest.graph_config ? (
                <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-96">
                  {JSON.stringify(backtest.graph_config, null, 2)}
                </pre>
              ) : (
                <p className="text-muted-foreground">No graph configuration available</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Agent Models</CardTitle>
            </CardHeader>
            <CardContent>
              {backtest.agent_models && backtest.agent_models.length > 0 ? (
                <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-96">
                  {JSON.stringify(backtest.agent_models, null, 2)}
                </pre>
              ) : (
                <p className="text-muted-foreground">No agent model configuration available</p>
              )}
            </CardContent>
          </Card>

          {backtest.error_message && (
            <Card className="border-destructive">
              <CardHeader>
                <CardTitle className="text-destructive">Error</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs text-destructive bg-muted p-4 rounded-lg overflow-auto">
                  {backtest.error_message}
                </pre>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
