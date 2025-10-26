"""
Fetch S&P 500 constituents sorted by market cap
"""
import yfinance as yf
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup

print('Fetching S&P 500 constituents...')
print('=' * 80)

# Fetch with proper headers to avoid 403
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

try:
    response = requests.get(url, headers=headers)
    tables = pd.read_html(response.text, header=0)
    sp500_df = tables[0]

    # Get tickers
    tickers = sp500_df['Symbol'].tolist()
    print(f'Total S&P 500 companies: {len(tickers)}')

    # Clean tickers (replace . with -)
    tickers = [t.replace('.', '-') for t in tickers]

    print('\nFetching market cap for sorting (this will take 2-3 minutes)...')
    market_cap_data = []

    for i, ticker in enumerate(tickers):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            market_cap = info.get('marketCap', 0)

            market_cap_data.append({
                'ticker': ticker,
                'market_cap': market_cap,
                'name': info.get('longName', ticker)
            })

            if (i + 1) % 50 == 0:
                print(f'  Processed {i + 1}/{len(tickers)} tickers...')

            # Small delay to avoid rate limiting
            time.sleep(0.1)
        except Exception as e:
            print(f'  Warning: {ticker} - {str(e)[:50]}')
            market_cap_data.append({
                'ticker': ticker,
                'market_cap': 0,
                'name': ticker
            })

    # Sort by market cap (descending - largest first)
    df = pd.DataFrame(market_cap_data)
    df_sorted = df.sort_values('market_cap', ascending=False)

    # Save sorted list
    df_sorted.to_csv('sp500_sorted_by_marketcap.csv', index=False)
    print(f'\n✅ Saved sorted list to sp500_sorted_by_marketcap.csv')

    print('\n📊 Top 20 S&P 500 companies by market cap:')
    print('=' * 90)
    print(f'{"Rank":<6} {"Ticker":<8} {"Company":<45} {"Market Cap":<15}')
    print('-' * 90)

    for idx, (i, row) in enumerate(df_sorted.head(20).iterrows(), 1):
        market_cap_t = row['market_cap'] / 1e12
        market_cap_b = row['market_cap'] / 1e9

        if market_cap_t >= 1:
            cap_str = f'${market_cap_t:.2f}T'
        else:
            cap_str = f'${market_cap_b:.1f}B'

        name = row['name'][:43]
        print(f'{idx:<6} {row["ticker"]:<8} {name:<45} {cap_str:<15}')

    print('=' * 90)

    # Also save just the ticker list in order
    with open('sp500_tickers_sorted.txt', 'w') as f:
        for ticker in df_sorted['ticker'].tolist():
            f.write(f'{ticker}\n')

    print('✅ Saved ticker list to sp500_tickers_sorted.txt')

except Exception as e:
    print(f'Error: {e}')
    raise
