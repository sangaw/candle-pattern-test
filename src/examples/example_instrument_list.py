#!/usr/bin/env python3
"""
Example script demonstrating fetchInstrumentList function.
This fetches the complete instrument list from Kite Connect API.
"""
import sys
import os

# Import from parent directory (src)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_fetcher import KiteConnectDataFetcher

def main():
    """Demonstrate fetchInstrumentList functionality."""
    print("Instrument List Fetch Example")
    print("=" * 50)
    
    try:
        # Initialize the data fetcher
        fetcher = KiteConnectDataFetcher()
        
        print("Fetching complete instrument list from Kite Connect API...")
        print("This may take a few moments as it fetches all available instruments.")
        
        # Fetch instrument list
        df = fetcher.fetchInstrumentList(save_csv=True)
        
        if not df.empty:
            print(f"\n✓ Successfully fetched {len(df)} instruments")
            print(f"Data shape: {df.shape}")
            print(f"Columns available: {list(df.columns)}")
            
            # Display sample data
            print("\nSample instruments:")
            print(df.head(10))
            
            # Show statistics
            print(f"\nData summary:")
            print(f"  - Total instruments: {len(df):,}")
            
            # Exchange distribution
            if 'exchange' in df.columns:
                exchange_counts = df['exchange'].value_counts()
                print(f"  - Exchanges: {dict(exchange_counts)}")
            
            # Instrument type distribution
            if 'instrument_type' in df.columns:
                type_counts = df['instrument_type'].value_counts()
                print(f"  - Instrument types: {dict(type_counts)}")
            
            # Search for specific instruments
            print(f"\nSearch examples:")
            
            # Find NIFTY
            if 'tradingsymbol' in df.columns:
                nifty_instruments = df[df['tradingsymbol'].str.contains('NIFTY', case=False, na=False)]
                if not nifty_instruments.empty:
                    print(f"  - NIFTY instruments found: {len(nifty_instruments)}")
                    print(f"    Sample: {nifty_instruments[['tradingsymbol', 'instrument_token']].head(3).to_string()}")
            
            # Find BANKNIFTY
            if 'tradingsymbol' in df.columns:
                banknifty_instruments = df[df['tradingsymbol'].str.contains('BANKNIFTY', case=False, na=False)]
                if not banknifty_instruments.empty:
                    print(f"  - BANKNIFTY instruments found: {len(banknifty_instruments)}")
                    print(f"    Sample: {banknifty_instruments[['tradingsymbol', 'instrument_token']].head(3).to_string()}")
            
            # Find specific stock (e.g., RELIANCE)
            if 'tradingsymbol' in df.columns:
                reliance_instruments = df[df['tradingsymbol'].str.contains('RELIANCE', case=False, na=False)]
                if not reliance_instruments.empty:
                    print(f"  - RELIANCE instruments found: {len(reliance_instruments)}")
                    print(f"    Sample: {reliance_instruments[['tradingsymbol', 'instrument_token', 'exchange']].head(3).to_string()}")
            
            print(f"\n✓ CSV file saved in data/ folder with timestamp")
            print(f"  You can use this data to find instrument tokens for specific symbols")
            
        else:
            print("⚠ No instruments data returned")
            print("This might be due to:")
            print("  - Invalid API credentials")
            print("  - Network connectivity issues")
            print("  - API rate limiting")
        
        print("\n" + "=" * 50)
        print("Example completed!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    main() 