#!/usr/bin/env python3
"""
One-off script to run candlestick pattern analysis on a specified raw OHLC CSV file.
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from candlestick_patterns import CandlestickPatternAnalyzer

if len(sys.argv) < 2:
    print("Usage: python3 example_oneoff_pattern_analysis.py <input_csv_file>")
    sys.exit(1)

input_file = sys.argv[1]
if not os.path.exists(input_file):
    print(f"File not found: {input_file}")
    sys.exit(1)

analyzer = CandlestickPatternAnalyzer()
output_file = f"data/pattern_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

try:
    result_file = analyzer.process_csv_file(input_file_path=input_file, output_file_path=output_file)
    print(f"\n✓ Pattern analysis completed! Output: {result_file}")
    import pandas as pd
    df = pd.read_csv(result_file)
    print("\nSample of results (first 5 rows):")
    print(df[['Date', 'Open', 'High', 'Low', 'Close', 'pattern']].head().to_string(index=False))
    print("\nPattern Summary:")
    summary = analyzer.get_pattern_summary(df)
    for pattern, count in summary.items():
        if count > 0:
            print(f"  - {pattern}: {count} occurrences")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 