"""
Helper module to fetch financial statements from Yahoo Finance.
This module provides utilities to extract line items from yfinance data.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Optional


def fetch_financial_statements(ticker: str) -> Dict[str, List[Tuple[str, str, str, float, Optional[str]]]]:
    """
    Fetch all financial statements (Income Statement, Balance Sheet, Cash Flow) from Yahoo Finance.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dictionary with keys 'income_statement', 'balance_sheet', 'cash_flow'
        Each contains list of tuples: (line_item_name, report_period, period_type, value, currency)
    """
    try:
        stock = yf.Ticker(ticker)
        result = {
            'income_statement': [],
            'balance_sheet': [],
            'cash_flow': []
        }

        # Fetch annual financials
        result['income_statement'].extend(_process_statement(stock.financials, 'annual', 'USD'))
        result['balance_sheet'].extend(_process_statement(stock.balance_sheet, 'annual', 'USD'))
        result['cash_flow'].extend(_process_statement(stock.cashflow, 'annual', 'USD'))

        # Fetch quarterly financials
        result['income_statement'].extend(_process_statement(stock.quarterly_financials, 'quarterly', 'USD'))
        result['balance_sheet'].extend(_process_statement(stock.quarterly_balance_sheet, 'quarterly', 'USD'))
        result['cash_flow'].extend(_process_statement(stock.quarterly_cashflow, 'quarterly', 'USD'))

        return result

    except Exception as e:
        print(f"Error fetching financial statements for {ticker}: {e}")
        return {'income_statement': [], 'balance_sheet': [], 'cash_flow': []}


def _process_statement(df: pd.DataFrame, period_type: str, currency: str) -> List[Tuple[str, str, str, float, Optional[str]]]:
    """
    Process a financial statement DataFrame and extract line items.

    Args:
        df: DataFrame from yfinance (columns are dates, index is line item names)
        period_type: 'annual' or 'quarterly'
        currency: Currency code (e.g., 'USD')

    Returns:
        List of tuples: (line_item_name, report_period, period_type, value, currency)
    """
    result = []

    if df is None or df.empty:
        return result

    try:
        # Iterate through each column (date)
        for col in df.columns:
            # Extract date
            if isinstance(col, pd.Timestamp):
                report_period = col.strftime('%Y-%m-%d')
            else:
                report_period = str(col)[:10]  # Take first 10 chars (YYYY-MM-DD)

            # Iterate through each row (line item)
            for line_item_name in df.index:
                value = df.loc[line_item_name, col]

                # Skip NaN values
                if pd.isna(value):
                    continue

                # Convert to float
                try:
                    float_value = float(value)
                except (ValueError, TypeError):
                    continue

                result.append((
                    str(line_item_name),
                    report_period,
                    period_type,
                    float_value,
                    currency
                ))

    except Exception as e:
        print(f"Error processing statement: {e}")

    return result
