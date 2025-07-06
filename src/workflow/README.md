# Workflow Module

This module contains automated workflows for comprehensive data analysis processes.

## Files

### `nifty_data_analysis.py`
A comprehensive Python script that orchestrates the complete NIFTY data analysis workflow:

1. **Data Fetching**: Uses Kite Connect API to fetch NIFTY daily data for 2025
2. **Data Storage**: Saves the fetched data as CSV files with timestamps
3. **Pattern Analysis**: Analyzes candlestick patterns using the pattern recognition tools
4. **Report Generation**: Creates comprehensive analysis reports with visualizations

### `nifty_data_analysis.ipynb`
Jupyter notebook version of the same workflow for interactive execution and visualization.

## Features

- **Pydantic Integration**: Uses Pydantic models for data validation and type safety
- **Comprehensive Logging**: Detailed logging for debugging and monitoring
- **Error Handling**: Robust error handling with informative error messages
- **Data Validation**: Ensures data quality and format consistency
- **Flexible Output**: Saves results in multiple formats (CSV, logs, summaries)

## Usage

### Running the Python Script
```bash
cd src/workflow
python nifty_data_analysis.py
```

### Running the Jupyter Notebook
```bash
cd src/workflow
jupyter notebook nifty_data_analysis.ipynb
```

## Dependencies

- `pandas`: Data manipulation and analysis
- `pydantic`: Data validation and settings management
- `matplotlib` & `seaborn`: Data visualization
- `kiteconnect`: API integration for market data
- Custom modules: `data_fetcher`, `candlestick_patterns`

## Output Files

The workflow generates several output files in the `data/` directory:

1. **Raw Data CSV**: `nifty_daily_2025_YYYYMMDD_HHMMSS.csv`
2. **Pattern Analysis CSV**: `nifty_pattern_analysis_YYYYMMDD_HHMMSS.csv`
3. **Log Files**: `logs/nifty_analysis.log`

## Configuration

Ensure you have proper configuration in `config/local-settings.json` for Kite Connect API access.

## Example Output

```
NIFTY DATA ANALYSIS WORKFLOW COMPLETED
============================================================

NIFTY Candlestick Pattern Analysis Summary
==========================================

Data Overview:
- Total candles analyzed: 252
- Total patterns found: 45
- Pattern occurrence rate: 17.86%

Pattern Breakdown:
- doji: 12 occurrences
  Dates: 2025-01-15, 2025-02-03, 2025-03-10, 2025-04-22, 2025-05-08
  ... and 7 more
- hammer: 8 occurrences
  Dates: 2025-01-20, 2025-02-14, 2025-03-25, 2025-04-15, 2025-05-12
  ... and 3 more

Price Movement Analysis:
- Start price: 21500.00
- End price: 22850.00
- Total change: 1350.00 (+6.28%)
- Highest price: 23500.00
- Lowest price: 21000.00
============================================================ 