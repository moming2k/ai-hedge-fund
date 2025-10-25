import { useState } from "react";
import { BacktestHistoryList } from "./backtest-history-list";
import { BacktestDetailView } from "./backtest-detail-view";

export function BacktestHistory() {
  const [selectedBacktestId, setSelectedBacktestId] = useState<number | null>(null);

  const handleViewDetails = (backtestId: number) => {
    setSelectedBacktestId(backtestId);
  };

  const handleBack = () => {
    setSelectedBacktestId(null);
  };

  if (selectedBacktestId !== null) {
    return <BacktestDetailView backtestRunId={selectedBacktestId} onBack={handleBack} />;
  }

  return <BacktestHistoryList onViewDetails={handleViewDetails} />;
}
