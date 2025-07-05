#!/usr/bin/env python3
"""
Example script demonstrating candlestick pattern analysis on CSV files.
This script shows how to process NIFTY instrument data files and add pattern columns.
"""
import sys
import os
import glob
from datetime import datetime

# Import from parent directory (src)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from candlestick_patterns import CandlestickPatternAnalyzer

def main():
    """Demonstrate candlestick pattern analysis on CSV files."""
    print("Candlestick Pattern Analysis Example")
    print("=" * 50)
    
    try:
        # Initialize the pattern analyzer
        analyzer = CandlestickPatternAnalyzer()
        
        # Check if there are any NIFTY CSV files in the data directory
        data_dir = 'data'
        nifty_files = glob.glob(os.path.join(data_dir, "NIFTY_*.csv"))
        
        if not nifty_files:
            print("No NIFTY CSV files found in the data directory.")
            print("Please run the daily candles example first to generate data files.")
            return
        
        print(f"Found {len(nifty_files)} NIFTY CSV file(s):")
        for file in nifty_files:
            print(f"  - {os.path.basename(file)}")
        
        # Process the latest NIFTY file
        print(f"\nProcessing the latest NIFTY file...")
        output_file = analyzer.process_latest_nifty_file(data_dir)
        
        print(f"\n✓ Pattern analysis completed successfully!")
        print(f"Output file: {output_file}")
        
        # Show a sample of the results
        import pandas as pd
        result_df = pd.read_csv(output_file)
        
        print(f"\nSample of results (first 5 rows):")
        # Show the pattern column in the sample output
        print(result_df[['Date', 'Open', 'High', 'Low', 'Close', 'pattern']].head().to_string(index=False))
        # Show pattern summary
        pattern_summary = analyzer.get_pattern_summary(result_df)
        print(f"\nPattern Summary:")
        for pattern, count in pattern_summary.items():
            if count > 0:
                print(f"  - {pattern}: {count} occurrences")
        # Show specific pattern dates if any found
        for pattern in ['doji', 'hammer', 'bullish_engulfing', 'bearish_engulfing']:
            dates = analyzer.get_pattern_dates(result_df, pattern)
            if dates:
                print(f"\n{pattern} occurred on:")
                for date in dates[:5]:  # Show first 5 dates
                    print(f"  - {date}")
                if len(dates) > 5:
                    print(f"  ... and {len(dates) - 5} more dates")
        
        print("\n" + "=" * 50)
        print("Example completed!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

def process_specific_file():
    """Demonstrate processing a specific CSV file."""
    print("\nProcessing Specific File Example")
    print("=" * 50)
    
    try:
        # Initialize the pattern analyzer
        analyzer = CandlestickPatternAnalyzer()
        
        # Look for any CSV file in the data directory
        data_dir = 'data'
        csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
        
        if not csv_files:
            print("No CSV files found in the data directory.")
            return
        
        # Use the first CSV file found
        input_file = csv_files[0]
        print(f"Processing file: {os.path.basename(input_file)}")
        
        # Process with custom output filename
        output_file = analyzer.process_csv_file(
            input_file_path=input_file,
            output_file_path=f"data/pattern_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        print(f"✓ Analysis completed! Output: {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    main()
    process_specific_file() 