"""Repository layer for backtest operations"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from .models import BacktestRun, BacktestDailyResult


class BacktestRepository:
    """Repository for managing backtest runs and daily results"""

    @staticmethod
    def create_backtest_run(
        db: Session,
        tickers: List[str],
        start_date: date,
        end_date: date,
        initial_capital: float,
        graph_config: Optional[Dict[str, Any]] = None,
        agent_models: Optional[List[Dict[str, Any]]] = None,
        request_data: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> BacktestRun:
        """Create a new backtest run record"""
        backtest_run = BacktestRun(
            name=name,
            description=description,
            status="IN_PROGRESS",
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            graph_config=graph_config,
            agent_models=agent_models,
            request_data=request_data,
            started_at=datetime.utcnow(),
        )
        db.add(backtest_run)
        db.commit()
        db.refresh(backtest_run)
        return backtest_run

    @staticmethod
    def update_backtest_run_status(
        db: Session,
        backtest_run_id: int,
        status: str,
        final_portfolio_value: Optional[float] = None,
        total_return_pct: Optional[float] = None,
        sharpe_ratio: Optional[float] = None,
        sortino_ratio: Optional[float] = None,
        max_drawdown: Optional[float] = None,
        max_drawdown_date: Optional[date] = None,
        long_short_ratio: Optional[float] = None,
        gross_exposure: Optional[float] = None,
        net_exposure: Optional[float] = None,
        final_portfolio: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> BacktestRun:
        """Update backtest run with final results"""
        backtest_run = db.query(BacktestRun).filter(BacktestRun.id == backtest_run_id).first()
        if not backtest_run:
            raise ValueError(f"Backtest run {backtest_run_id} not found")

        backtest_run.status = status
        if status == "COMPLETE":
            backtest_run.completed_at = datetime.utcnow()

        if final_portfolio_value is not None:
            backtest_run.final_portfolio_value = final_portfolio_value
        if total_return_pct is not None:
            backtest_run.total_return_pct = total_return_pct
        if sharpe_ratio is not None:
            backtest_run.sharpe_ratio = sharpe_ratio
        if sortino_ratio is not None:
            backtest_run.sortino_ratio = sortino_ratio
        if max_drawdown is not None:
            backtest_run.max_drawdown = max_drawdown
        if max_drawdown_date is not None:
            backtest_run.max_drawdown_date = max_drawdown_date
        if long_short_ratio is not None:
            backtest_run.long_short_ratio = long_short_ratio
        if gross_exposure is not None:
            backtest_run.gross_exposure = gross_exposure
        if net_exposure is not None:
            backtest_run.net_exposure = net_exposure
        if final_portfolio is not None:
            backtest_run.final_portfolio = final_portfolio
        if error_message is not None:
            backtest_run.error_message = error_message

        db.commit()
        db.refresh(backtest_run)
        return backtest_run

    @staticmethod
    def add_daily_result(
        db: Session,
        backtest_run_id: int,
        date: date,
        portfolio_value: float,
        cash: float,
        decisions: Optional[Dict[str, Any]] = None,
        executed_trades: Optional[Dict[str, Any]] = None,
        analyst_signals: Optional[Dict[str, Any]] = None,
        current_prices: Optional[Dict[str, float]] = None,
        long_exposure: Optional[float] = None,
        short_exposure: Optional[float] = None,
        gross_exposure: Optional[float] = None,
        net_exposure: Optional[float] = None,
        long_short_ratio: Optional[float] = None,
        portfolio_return_pct: Optional[float] = None,
    ) -> BacktestDailyResult:
        """Add a daily result for a backtest run"""
        daily_result = BacktestDailyResult(
            backtest_run_id=backtest_run_id,
            date=date,
            portfolio_value=portfolio_value,
            cash=cash,
            decisions=decisions,
            executed_trades=executed_trades,
            analyst_signals=analyst_signals,
            current_prices=current_prices,
            long_exposure=long_exposure,
            short_exposure=short_exposure,
            gross_exposure=gross_exposure,
            net_exposure=net_exposure,
            long_short_ratio=long_short_ratio,
            portfolio_return_pct=portfolio_return_pct,
        )
        db.add(daily_result)
        db.commit()
        db.refresh(daily_result)
        return daily_result

    @staticmethod
    def get_backtest_run(db: Session, backtest_run_id: int) -> Optional[BacktestRun]:
        """Get a backtest run by ID"""
        return db.query(BacktestRun).filter(BacktestRun.id == backtest_run_id).first()

    @staticmethod
    def get_all_backtest_runs(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        ticker: Optional[str] = None,
    ) -> List[BacktestRun]:
        """Get all backtest runs with optional filtering"""
        query = db.query(BacktestRun)

        if status:
            query = query.filter(BacktestRun.status == status)

        if ticker:
            # Filter runs that include the specified ticker (JSON array contains)
            query = query.filter(BacktestRun.tickers.contains([ticker]))

        query = query.order_by(desc(BacktestRun.created_at))
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_daily_results(
        db: Session,
        backtest_run_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[BacktestDailyResult]:
        """Get daily results for a backtest run"""
        query = db.query(BacktestDailyResult).filter(
            BacktestDailyResult.backtest_run_id == backtest_run_id
        )

        if start_date:
            query = query.filter(BacktestDailyResult.date >= start_date)
        if end_date:
            query = query.filter(BacktestDailyResult.date <= end_date)

        return query.order_by(BacktestDailyResult.date).all()

    @staticmethod
    def delete_backtest_run(db: Session, backtest_run_id: int) -> bool:
        """Delete a backtest run and all its daily results (cascade)"""
        backtest_run = db.query(BacktestRun).filter(BacktestRun.id == backtest_run_id).first()
        if not backtest_run:
            return False

        db.delete(backtest_run)
        db.commit()
        return True

    @staticmethod
    def count_backtest_runs(
        db: Session,
        status: Optional[str] = None,
        ticker: Optional[str] = None,
    ) -> int:
        """Count total backtest runs with optional filtering"""
        query = db.query(BacktestRun)

        if status:
            query = query.filter(BacktestRun.status == status)

        if ticker:
            query = query.filter(BacktestRun.tickers.contains([ticker]))

        return query.count()
