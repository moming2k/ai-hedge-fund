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
import { Trash2, Eye, TrendingUp, TrendingDown, AlertCircle, Loader2 } from "lucide-react";
import { backtestResultsApi, BacktestRunSummary } from "@/services/backtest-results-api";
import { toast } from "sonner";

interface BacktestHistoryListProps {
  onViewDetails: (backtestRunId: number) => void;
}

export function BacktestHistoryList({ onViewDetails }: BacktestHistoryListProps) {
  const [runs, setRuns] = useState<BacktestRunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "COMPLETE" | "ERROR" | "IN_PROGRESS">("all");
  const [deleting, setDeleting] = useState<number | null>(null);

  useEffect(() => {
    loadBacktestRuns();
  }, [filter]);

  const loadBacktestRuns = async () => {
    setLoading(true);
    try {
      const params = filter === "all" ? {} : { status: filter };
      const response = await backtestResultsApi.listBacktestRuns({ ...params, limit: 100 });
      setRuns(response.runs);
    } catch (error) {
      console.error("Failed to load backtest runs:", error);
      toast.error("Failed to load backtest history");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number, event: React.MouseEvent) => {
    event.stopPropagation();

    if (!confirm("Are you sure you want to delete this backtest run? This action cannot be undone.")) {
      return;
    }

    setDeleting(id);
    try {
      await backtestResultsApi.deleteBacktestRun(id);
      toast.success("Backtest run deleted successfully");
      // Remove from list
      setRuns(runs.filter(run => run.id !== id));
    } catch (error) {
      console.error("Failed to delete backtest run:", error);
      toast.error("Failed to delete backtest run");
    } finally {
      setDeleting(null);
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleDateString();
  };

  const formatDateTime = (dateStr: string | null) => {
    if (!dateStr) return "N/A";
    return new Date(dateStr).toLocaleString();
  };

  const formatNumber = (num: number | null, decimals: number = 2) => {
    if (num === null) return "N/A";
    return num.toFixed(decimals);
  };

  const formatCurrency = (num: number | null) => {
    if (num === null) return "N/A";
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

  const getReturnColor = (returnPct: number | null) => {
    if (returnPct === null) return "text-muted-foreground";
    return returnPct > 0 ? "text-green-600 dark:text-green-400" : returnPct < 0 ? "text-red-600 dark:text-red-400" : "text-muted-foreground";
  };

  const getReturnIcon = (returnPct: number | null) => {
    if (returnPct === null) return null;
    return returnPct > 0 ? <TrendingUp className="w-4 h-4" /> : returnPct < 0 ? <TrendingDown className="w-4 h-4" /> : null;
  };

  const filteredRuns = filter === "all" ? runs : runs.filter(run => run.status === filter);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Backtest History</CardTitle>
          <CardDescription>
            View and analyze your historical backtest runs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={filter} onValueChange={(value) => setFilter(value as any)} className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">All ({runs.length})</TabsTrigger>
              <TabsTrigger value="COMPLETE">
                Completed ({runs.filter(r => r.status === "COMPLETE").length})
              </TabsTrigger>
              <TabsTrigger value="IN_PROGRESS">
                Running ({runs.filter(r => r.status === "IN_PROGRESS").length})
              </TabsTrigger>
              <TabsTrigger value="ERROR">
                Errors ({runs.filter(r => r.status === "ERROR").length})
              </TabsTrigger>
            </TabsList>

            <TabsContent value={filter} className="mt-4">
              {filteredRuns.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No backtest runs found</p>
                  <p className="text-sm mt-2">Run a backtest to see it here</p>
                </div>
              ) : (
                <div className="border rounded-lg">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name / Tickers</TableHead>
                        <TableHead>Period</TableHead>
                        <TableHead className="text-right">Return</TableHead>
                        <TableHead className="text-right">Sharpe</TableHead>
                        <TableHead className="text-right">Max DD</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Created</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredRuns.map((run) => (
                        <TableRow
                          key={run.id}
                          className="cursor-pointer hover:bg-accent/50"
                          onClick={() => onViewDetails(run.id)}
                        >
                          <TableCell>
                            <div>
                              <div className="font-medium">
                                {run.name || `Backtest #${run.id}`}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {run.tickers.join(", ")}
                              </div>
                            </div>
                          </TableCell>
                          <TableCell className="text-sm">
                            <div>{formatDate(run.start_date)}</div>
                            <div className="text-muted-foreground">to {formatDate(run.end_date)}</div>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className={`flex items-center justify-end gap-1 font-medium ${getReturnColor(run.total_return_pct)}`}>
                              {getReturnIcon(run.total_return_pct)}
                              <span>{formatNumber(run.total_return_pct)}%</span>
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {formatCurrency(run.final_portfolio_value)}
                            </div>
                          </TableCell>
                          <TableCell className="text-right font-medium">
                            {formatNumber(run.sharpe_ratio)}
                          </TableCell>
                          <TableCell className="text-right font-medium text-red-600 dark:text-red-400">
                            {formatNumber(run.max_drawdown)}%
                          </TableCell>
                          <TableCell>
                            {getStatusBadge(run.status)}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {formatDateTime(run.created_at)}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  onViewDetails(run.id);
                                }}
                              >
                                <Eye className="w-4 h-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => handleDelete(run.id, e)}
                                disabled={deleting === run.id}
                              >
                                {deleting === run.id ? (
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                ) : (
                                  <Trash2 className="w-4 h-4 text-destructive" />
                                )}
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
