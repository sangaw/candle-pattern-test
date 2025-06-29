#!/usr/bin/env python3
"""
Example script demonstrating fetchHistoricalCandles function.
This replicates the curl command example for NSE-ACC minute candles.
"""
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_fetcher import KiteConnectDataFetcher

def main():
    """Demonstrate fetchHistoricalCandles functionality."""
    print("Historical Candles Fetch Example")
    print("=" * 50)
    
    try:
        # Initialize the data fetcher
        fetcher = KiteConnectDataFetcher()
        
        # Example 1: NSE-ACC minute candles (as per the curl example)
        print("\n1. NSE-ACC Minute Candles (2017-12-15 09:15:00 to 09:20:00)")
        print("-" * 60)
        
        instrument_token = 5633  # NSE-ACC
        from_datetime = "2017-12-15 09:15:00"
        to_datetime = "2017-12-15 09:20:00"
        interval = "minute"
        
        print(f"Instrument Token: {instrument_token}")
        print(f"From: {from_datetime}")
        print(f"To: {to_datetime}")
        print(f"Interval: {interval}")
        
        df = fetcher.fetchHistoricalCandles(instrument_token, from_datetime, to_datetime, interval)
        
        if not df.empty:
            print(f"\n✓ Successfully fetched {len(df)} candles")
            print(f"Date range: {df['date'].min()} to {df['date'].max()}")
            print("\nSample data:")
            print(df.head())
            print(f"\nData summary:")
            print(f"  - Total candles: {len(df)}")
            print(f"  - Price range: {df['low'].min():.2f} - {df['high'].max():.2f}")
            print(f"  - Total volume: {df['volume'].sum():,}")
        else:
            print("⚠ No data returned - this might be expected for historical data outside trading hours")
        
        # Example 2: NIFTY day candles for recent data
        print("\n\n2. NIFTY Day Candles (Recent)")
        print("-" * 60)
        
        # Get NIFTY instrument token from config
        kite_config = fetcher.config.get('kite_connect', {})
        nifty_token = kite_config.get('nifty_instrument_token', 256265)
        
        # Use recent dates
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        
        from_date = yesterday.strftime("%Y-%m-%d 09:15:00")
        to_date = today.strftime("%Y-%m-%d 15:30:00")
        
        print(f"Instrument Token: {nifty_token} (NIFTY)")
        print(f"From: {from_date}")
        print(f"To: {to_date}")
        print(f"Interval: day")
        
        df_nifty = fetcher.fetchHistoricalCandles(nifty_token, from_date, to_date, "day")
        
        if not df_nifty.empty:
            print(f"\n✓ Successfully fetched {len(df_nifty)} candles")
            print(f"Date range: {df_nifty['date'].min()} to {df_nifty['date'].max()}")
            print("\nSample data:")
            print(df_nifty.head())
        else:
            print("⚠ No data returned")
        
        # Example 3: Different intervals
        print("\n\n3. Different Intervals Example")
        print("-" * 60)
        
        intervals = ["5minute", "15minute", "30minute"]
        test_from = "2024-01-15 09:15:00"
        test_to = "2024-01-15 10:00:00"
        
        for interval in intervals:
            print(f"\nTesting interval: {interval}")
            df_test = fetcher.fetchHistoricalCandles(nifty_token, test_from, test_to, interval)
            
            if not df_test.empty:
                print(f"  ✓ Fetched {len(df_test)} candles")
                print(f"  Time range: {df_test['date'].min()} to {df_test['date'].max()}")
            else:
                print(f"  ⚠ No data for {interval}")
        
        print("\n" + "=" * 50)
        print("Example completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    main() 