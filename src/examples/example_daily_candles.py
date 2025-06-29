#!/usr/bin/env python3
"""
Example script demonstrating fetchDailyCandlesForInstruments function.
This fetches daily candles for all instruments listed in config/instrumentlist.json.
"""
import sys
import os
from datetime import datetime, timedelta

# Import from parent directory (src)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_fetcher import KiteConnectDataFetcher

def main():
    """Demonstrate fetchDailyCandlesForInstruments functionality."""
    print("Daily Candles for Instruments Example")
    print("=" * 50)
    
    try:
        # Initialize the data fetcher
        fetcher = KiteConnectDataFetcher()
        
        # Define date range (last 30 days)
        to_date = datetime.now().date() - timedelta(days=1)  # Yesterday
        from_date = to_date - timedelta(days=30)  # 30 days before yesterday
        
        print(f"Fetching daily candles for instruments from {from_date} to {to_date}")
        print("Instruments configured in config/instrumentlist.json:")
        print("  - NIFTY")
        print("  - BANKNIFTY") 
        print("  - INFOSYS")
        print("  - RELIANCE")
        print()
        
        # Fetch daily candles for all configured instruments
        results = fetcher.fetchDailyCandlesForInstruments(
            from_date=str(from_date),
            to_date=str(to_date)
        )
        
        if results:
            print(f"\n✓ Successfully fetched data for {len(results)} instruments")
            print(f"Results summary:")
            
            for instrument_name, df in results.items():
                print(f"\n{instrument_name}:")
                print(f"  - Candles: {len(df)}")
                print(f"  - Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
                print(f"  - Price range: ₹{df['low'].min():.2f} - ₹{df['high'].max():.2f}")
                print(f"  - Last close: ₹{df['close'].iloc[-1]:.2f}")
                print(f"  - Total volume: {df['volume'].sum():,}")
                
                # Calculate some basic statistics
                if len(df) > 1:
                    returns = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
                    print(f"  - Period return: {returns:.2f}%")
                    
                    avg_volume = df['volume'].mean()
                    print(f"  - Average daily volume: {avg_volume:,.0f}")
                
                # Show sample data
                print(f"  - Sample data (last 3 days):")
                print(df[['date', 'open', 'high', 'low', 'close', 'volume']].tail(3).to_string(index=False))
            
            print(f"\n✓ CSV files saved in data/ folder with naming pattern:")
            print(f"  {{instrument_name}}_{{from_date}}_to_{to_date}_{{timestamp}}.csv")
            
            # List the created files
            import glob
            csv_files = glob.glob(f"data/*_{from_date}_to_{to_date}_*.csv")
            if csv_files:
                print(f"\nCreated files:")
                for f in csv_files:
                    print(f"  - {os.path.basename(f)}")
            
        else:
            print("⚠ No data returned for any instruments")
            print("This might be due to:")
            print("  - Invalid API credentials")
            print("  - Network connectivity issues")
            print("  - No trading data available for the specified date range")
            print("  - Instruments not found in the instrument list")
        
        print("\n" + "=" * 50)
        print("Example completed!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    main() 