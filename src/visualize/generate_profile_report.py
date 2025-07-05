#!/usr/bin/env python3
"""
Generate ydata-profiling report for CSV files and save to data folder.
"""
import sys
import os
import pandas as pd
from ydata_profiling import ProfileReport
import webbrowser

def generate_profile_report(csv_path, output_name=None):
    """
    Generate a ydata-profiling report for a CSV file.
    
    Args:
        csv_path (str): Path to the CSV file
        output_name (str): Name for the output HTML file (without extension)
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        return
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Generate output filename
    if output_name is None:
        base_name = os.path.splitext(os.path.basename(csv_path))[0]
        output_name = f"{base_name}_profile"
    
    output_html = f"data/{output_name}.html"
    
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} records")
    
    print("Generating profile report...")
    profile = ProfileReport(df, title=f"{output_name.replace('_', ' ').title()} Profile", explorative=True)
    profile.to_file(output_html)
    
    print(f"Profile report saved as {output_html}")
    
    # Open in browser
    webbrowser.open('file://' + os.path.realpath(output_html))
    
    return output_html

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python generate_profile_report.py <csv_file> [output_name]")
        print("Example: python generate_profile_report.py data/instruments_list_20250705_093603.csv")
        return
    
    csv_path = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        generate_profile_report(csv_path, output_name)
    except Exception as e:
        print(f"Error generating profile report: {str(e)}")
        print("Make sure ydata-profiling is installed: pip install ydata-profiling")

if __name__ == "__main__":
    main() 