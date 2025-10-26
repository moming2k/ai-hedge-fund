#!/usr/bin/env python3
"""
Fetch comprehensive S&P 500 company information and save to data/sp500.csv
"""
import yfinance as yf
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
from pathlib import Path

print('Fetching S&P 500 company information...')
print('=' * 80)

# Fetch S&P 500 constituents from Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

try:
    response = requests.get(url, headers=headers)
    tables = pd.read_html(response.text, header=0)
    sp500_df = tables[0]

    # Get basic info from Wikipedia table
    print(f'Fetched {len(sp500_df)} companies from Wikipedia')

    # Prepare data storage
    company_data = []

    print('\nFetching detailed company information from Yahoo Finance...')
    print('This will take several minutes (~5-7 min for all 503 companies)...\n')

    for idx, row in sp500_df.iterrows():
        ticker_raw = row['Symbol']
        ticker = ticker_raw.replace('.', '-')  # Yahoo Finance format

        try:
            # Fetch detailed info from Yahoo Finance
            stock = yf.Ticker(ticker)
            info = stock.info

            # Compile comprehensive company data
            company_info = {
                # Basic identification
                'ticker': ticker,
                'company_name': info.get('longName', row.get('Security', '')),
                'sector': row.get('GICS Sector', ''),
                'industry': row.get('GICS Sub-Industry', ''),
                'headquarters': row.get('Headquarters Location', ''),
                'date_added': row.get('Date added', ''),
                'cik': row.get('CIK', ''),
                'founded': row.get('Founded', ''),

                # Market data
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'current_price': info.get('currentPrice', 0),
                'previous_close': info.get('previousClose', 0),
                'open': info.get('open', 0),
                'day_low': info.get('dayLow', 0),
                'day_high': info.get('dayHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'volume': info.get('volume', 0),
                'avg_volume': info.get('averageVolume', 0),

                # Valuation ratios
                'pe_ratio': info.get('trailingPE', 0),
                'forward_pe': info.get('forwardPE', 0),
                'peg_ratio': info.get('pegRatio', 0),
                'price_to_book': info.get('priceToBook', 0),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
                'ev_to_revenue': info.get('enterpriseToRevenue', 0),
                'ev_to_ebitda': info.get('enterpriseToEbitda', 0),

                # Profitability metrics
                'profit_margin': info.get('profitMargins', 0),
                'operating_margin': info.get('operatingMargins', 0),
                'gross_margin': info.get('grossMargins', 0),
                'roe': info.get('returnOnEquity', 0),
                'roa': info.get('returnOnAssets', 0),

                # Financial metrics
                'revenue': info.get('totalRevenue', 0),
                'revenue_per_share': info.get('revenuePerShare', 0),
                'earnings': info.get('netIncomeToCommon', 0),
                'eps': info.get('trailingEps', 0),
                'forward_eps': info.get('forwardEps', 0),
                'total_cash': info.get('totalCash', 0),
                'total_debt': info.get('totalDebt', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'quick_ratio': info.get('quickRatio', 0),

                # Growth metrics
                'revenue_growth': info.get('revenueGrowth', 0),
                'earnings_growth': info.get('earningsGrowth', 0),

                # Dividend information
                'dividend_rate': info.get('dividendRate', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'payout_ratio': info.get('payoutRatio', 0),

                # Other
                'beta': info.get('beta', 0),
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'float_shares': info.get('floatShares', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'website': info.get('website', ''),
                'business_summary': info.get('longBusinessSummary', '')[:500] if info.get('longBusinessSummary') else '',  # Limit to 500 chars
            }

            company_data.append(company_info)

            # Progress indicator
            if (idx + 1) % 25 == 0:
                print(f'  Processed {idx + 1}/{len(sp500_df)} companies... (Latest: {ticker})')

            # Rate limiting
            time.sleep(0.1)

        except Exception as e:
            print(f'  Warning: Failed to fetch data for {ticker}: {str(e)[:50]}')
            # Add minimal data
            company_data.append({
                'ticker': ticker,
                'company_name': row.get('Security', ''),
                'sector': row.get('GICS Sector', ''),
                'industry': row.get('GICS Sub-Industry', ''),
                'headquarters': row.get('Headquarters Location', ''),
                'date_added': row.get('Date added', ''),
                'cik': row.get('CIK', ''),
                'founded': row.get('Founded', ''),
            })

    # Create DataFrame and save to CSV
    df = pd.DataFrame(company_data)

    # Sort by market cap (descending)
    df_sorted = df.sort_values('market_cap', ascending=False)

    # Ensure data directory exists
    Path('data').mkdir(exist_ok=True)

    # Save to CSV
    output_path = 'data/sp500.csv'
    df_sorted.to_csv(output_path, index=False)

    print(f'\n✅ Successfully saved {len(df_sorted)} companies to {output_path}')
    print(f'\nTop 10 companies by market cap:')
    print('=' * 90)

    for idx, row in df_sorted.head(10).iterrows():
        market_cap_t = row['market_cap'] / 1e12
        market_cap_b = row['market_cap'] / 1e9

        if market_cap_t >= 1:
            cap_str = f'${market_cap_t:.2f}T'
        else:
            cap_str = f'${market_cap_b:.1f}B'

        print(f"{row['ticker']:<8} {row['company_name'][:40]:<42} {cap_str}")

    print('=' * 90)
    print(f'\nData columns: {len(df_sorted.columns)}')
    print(f'Sample columns: {", ".join(df_sorted.columns[:10].tolist())}...')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
    raise
