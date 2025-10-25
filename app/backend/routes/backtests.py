"""API routes for managing and viewing backtest results"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.backend.database import get_db
from app.backend.database.backtest_repository import BacktestRepository
from app.backend.models.schemas import (
    BacktestRunSummaryResponse,
    BacktestRunDetailResponse,
    BacktestDailyResultResponse,
    BacktestRunsListResponse,
    ErrorResponse,
)

router = APIRouter(prefix="/backtests")


@router.get(
    "",
    response_model=BacktestRunsListResponse,
    responses={
        200: {"description": "List of backtest runs"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def list_backtest_runs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status (IDLE, IN_PROGRESS, COMPLETE, ERROR)"),
    ticker: Optional[str] = Query(None, description="Filter by ticker symbol"),
    db: Session = Depends(get_db),
):
    """
    Get a paginated list of backtest runs with optional filtering.

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    - **status**: Filter by status (IDLE, IN_PROGRESS, COMPLETE, ERROR)
    - **ticker**: Filter by ticker symbol
    """
    try:
        runs = BacktestRepository.get_all_backtest_runs(
            db=db,
            skip=skip,
            limit=limit,
            status=status,
            ticker=ticker,
        )
        total = BacktestRepository.count_backtest_runs(
            db=db,
            status=status,
            ticker=ticker,
        )

        # Convert database models to response models
        run_summaries = []
        for run in runs:
            run_summaries.append(
                BacktestRunSummaryResponse(
                    id=run.id,
                    name=run.name,
                    description=run.description,
                    status=run.status,
                    tickers=run.tickers,
                    start_date=run.start_date.isoformat() if run.start_date else None,
                    end_date=run.end_date.isoformat() if run.end_date else None,
                    initial_capital=run.initial_capital,
                    final_portfolio_value=run.final_portfolio_value,
                    total_return_pct=run.total_return_pct,
                    sharpe_ratio=run.sharpe_ratio,
                    sortino_ratio=run.sortino_ratio,
                    max_drawdown=run.max_drawdown,
                    max_drawdown_date=run.max_drawdown_date.isoformat() if run.max_drawdown_date else None,
                    long_short_ratio=run.long_short_ratio,
                    gross_exposure=run.gross_exposure,
                    net_exposure=run.net_exposure,
                    created_at=run.created_at,
                    started_at=run.started_at,
                    completed_at=run.completed_at,
                    error_message=run.error_message,
                )
            )

        return BacktestRunsListResponse(
            total=total,
            skip=skip,
            limit=limit,
            runs=run_summaries,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve backtest runs: {str(e)}")


@router.get(
    "/{backtest_run_id}",
    response_model=BacktestRunDetailResponse,
    responses={
        200: {"description": "Backtest run details"},
        404: {"model": ErrorResponse, "description": "Backtest run not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_backtest_run(
    backtest_run_id: int,
    include_daily_results: bool = Query(True, description="Include daily results in the response"),
    db: Session = Depends(get_db),
):
    """
    Get detailed information about a specific backtest run.

    - **backtest_run_id**: The ID of the backtest run
    - **include_daily_results**: Whether to include daily results (default: True)
    """
    try:
        run = BacktestRepository.get_backtest_run(db=db, backtest_run_id=backtest_run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Backtest run {backtest_run_id} not found")

        # Get daily results if requested
        daily_results = None
        if include_daily_results:
            daily_results_models = BacktestRepository.get_daily_results(
                db=db,
                backtest_run_id=backtest_run_id,
            )
            daily_results = [
                BacktestDailyResultResponse(
                    id=result.id,
                    backtest_run_id=result.backtest_run_id,
                    date=result.date.isoformat() if result.date else None,
                    portfolio_value=result.portfolio_value,
                    cash=result.cash,
                    decisions=result.decisions,
                    executed_trades=result.executed_trades,
                    analyst_signals=result.analyst_signals,
                    current_prices=result.current_prices,
                    long_exposure=result.long_exposure,
                    short_exposure=result.short_exposure,
                    gross_exposure=result.gross_exposure,
                    net_exposure=result.net_exposure,
                    long_short_ratio=result.long_short_ratio,
                    portfolio_return_pct=result.portfolio_return_pct,
                    created_at=result.created_at,
                )
                for result in daily_results_models
            ]

        return BacktestRunDetailResponse(
            id=run.id,
            name=run.name,
            description=run.description,
            status=run.status,
            tickers=run.tickers,
            start_date=run.start_date.isoformat() if run.start_date else None,
            end_date=run.end_date.isoformat() if run.end_date else None,
            initial_capital=run.initial_capital,
            final_portfolio_value=run.final_portfolio_value,
            total_return_pct=run.total_return_pct,
            sharpe_ratio=run.sharpe_ratio,
            sortino_ratio=run.sortino_ratio,
            max_drawdown=run.max_drawdown,
            max_drawdown_date=run.max_drawdown_date.isoformat() if run.max_drawdown_date else None,
            long_short_ratio=run.long_short_ratio,
            gross_exposure=run.gross_exposure,
            net_exposure=run.net_exposure,
            graph_config=run.graph_config,
            agent_models=run.agent_models,
            request_data=run.request_data,
            final_portfolio=run.final_portfolio,
            created_at=run.created_at,
            started_at=run.started_at,
            completed_at=run.completed_at,
            error_message=run.error_message,
            daily_results=daily_results,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve backtest run: {str(e)}")


@router.get(
    "/{backtest_run_id}/daily",
    response_model=list[BacktestDailyResultResponse],
    responses={
        200: {"description": "Daily results for the backtest run"},
        404: {"model": ErrorResponse, "description": "Backtest run not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_backtest_daily_results(
    backtest_run_id: int,
    start_date: Optional[str] = Query(None, description="Filter from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter to this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """
    Get daily results for a specific backtest run with optional date filtering.

    - **backtest_run_id**: The ID of the backtest run
    - **start_date**: Filter results from this date (inclusive)
    - **end_date**: Filter results to this date (inclusive)
    """
    try:
        # Check if backtest run exists
        run = BacktestRepository.get_backtest_run(db=db, backtest_run_id=backtest_run_id)
        if not run:
            raise HTTPException(status_code=404, detail=f"Backtest run {backtest_run_id} not found")

        # Parse dates if provided
        start_date_obj = None
        end_date_obj = None
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

        # Get daily results
        daily_results_models = BacktestRepository.get_daily_results(
            db=db,
            backtest_run_id=backtest_run_id,
            start_date=start_date_obj,
            end_date=end_date_obj,
        )

        return [
            BacktestDailyResultResponse(
                id=result.id,
                backtest_run_id=result.backtest_run_id,
                date=result.date.isoformat() if result.date else None,
                portfolio_value=result.portfolio_value,
                cash=result.cash,
                decisions=result.decisions,
                executed_trades=result.executed_trades,
                analyst_signals=result.analyst_signals,
                current_prices=result.current_prices,
                long_exposure=result.long_exposure,
                short_exposure=result.short_exposure,
                gross_exposure=result.gross_exposure,
                net_exposure=result.net_exposure,
                long_short_ratio=result.long_short_ratio,
                portfolio_return_pct=result.portfolio_return_pct,
                created_at=result.created_at,
            )
            for result in daily_results_models
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve daily results: {str(e)}")


@router.delete(
    "/{backtest_run_id}",
    responses={
        200: {"description": "Backtest run deleted successfully"},
        404: {"model": ErrorResponse, "description": "Backtest run not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_backtest_run(
    backtest_run_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a backtest run and all its daily results.

    - **backtest_run_id**: The ID of the backtest run to delete
    """
    try:
        success = BacktestRepository.delete_backtest_run(db=db, backtest_run_id=backtest_run_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Backtest run {backtest_run_id} not found")

        return {"message": f"Backtest run {backtest_run_id} deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete backtest run: {str(e)}")
