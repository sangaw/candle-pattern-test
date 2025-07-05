# NIFTY Candlestick Pattern Tester

This project analyzes NIFTY and other instrument candlestick patterns using the Kite Connect API. It supports robust data fetching, token management, SHA-256 hashing, CSV export, comprehensive visualization tools, and detailed analysis with both interactive web interfaces and automated reports.

## 🚀 Features
- **Data Fetching**: Fetch historical OHLC (Open, High, Low, Close) data for NIFTY and any instrument on Kite Connect
- **Automatic Token Management**: Automatic token refresh and validation for Kite Connect API
- **SHA-256 Authentication**: Secure API authentication with SHA-256 hash generation
- **CSV Export**: Save fetched data as CSV files in the `data/` folder
- **Instrument List Management**: Fetch and export the complete instrument list from Kite Connect
- **Multi-Instrument Support**: Fetch daily candles for a configurable list of instruments
- **📊 Advanced Visualization**: Interactive web-based CSV viewer with filtering and search
- **📈 Data Profiling**: Automated ydata-profiling reports for comprehensive data analysis
- **🔍 Pattern Analysis**: Candlestick pattern recognition with single-column output
- **📝 Comprehensive Logging**: Detailed logging to `logs/data_fetcher.log`
- **🧪 Extensive Testing**: Comprehensive test suite with examples
- **🎯 One-off Analysis**: Run pattern analysis on any CSV file

## 📁 Project Structure
```
candle-pattern-test/
├── config/
│   ├── local-settings.json     # Kite Connect API configuration
│   └── instrumentlist.json     # List of instruments to fetch daily candles for
├── data/                       # All fetched CSV data and reports
│   ├── *.csv                   # Historical data files
│   ├── *_profile.html          # ydata-profiling reports
│   └── pattern_analysis_*.csv  # Pattern analysis results
├── logs/
│   └── data_fetcher.log        # Log file for all data fetching operations
├── src/
│   ├── auth/                   # Token management and authentication
│   ├── examples/               # Example scripts
│   ├── visualize/              # 🆕 Visualization module
│   │   ├── __init__.py
│   │   ├── unified_csv_viewer.py      # Combined Flask + ydata-profiling viewer
│   │   ├── generate_profile_report.py # Standalone ydata-profiling generator
│   │   └── visualize_csv_profile.py   # Original Flask interactive viewer
│   ├── candlestick_patterns.py
│   ├── data_fetcher.py         # Main data fetching logic
│   └── utils.py
├── tests/                      # Test suite
├── requirements.txt
└── README.md
```

## 🔄 Data Flow Diagram

```mermaid
graph TD
    A[Kite Connect API] --> B[Data Fetcher]
    B --> C[CSV Files in data/]
    C --> D[Visualization Module]
    
    D --> E[Flask Interactive Viewer]
    D --> F[ydata-Profiling Reports]
    
    E --> G[Filter by Name]
    E --> H[Search by Symbol]
    E --> I[Statistics Dashboard]
    
    F --> J[Data Quality Analysis]
    F --> K[Correlation Matrices]
    F --> L[Distribution Charts]
    
    C --> M[Pattern Analysis]
    M --> N[Single Column Pattern Output]
    N --> O[Pattern Analysis CSV]
    
    subgraph "Interactive Features"
        G
        H
        I
    end
    
    subgraph "Automated Analysis"
        J
        K
        L
    end
    
    subgraph "Pattern Recognition"
        M
        N
        O
    end
```

## 🎯 Visualization Features

### **📊 Unified CSV Viewer**
The main visualization tool that combines interactive web interface with automated data profiling:

```bash
# Start interactive viewer
python src/visualize/unified_csv_viewer.py data/instruments_list_20250705_093603.csv

# Generate profile report only
python src/visualize/unified_csv_viewer.py data/instruments_list_20250705_093603.csv --profile-only

# Use custom port
python src/visualize/unified_csv_viewer.py data/instruments_list_20250705_093603.csv --port 8080
```

**Features:**
- **🔍 Interactive Filtering**: Dropdown with 11,731+ unique instrument names
- **🔎 Real-time Search**: Search across trading symbols and names
- **📈 Live Statistics**: Total, filtered, and displayed record counts
- **📊 One-click Profiling**: Generate detailed ydata-profiling reports
- **📥 Data Export**: Download filtered CSV data
- **📱 Responsive Design**: Works on desktop and mobile browsers

### **📈 ydata-Profiling Reports**
Automated comprehensive data analysis reports:

```bash
# Generate standalone profile report
python src/visualize/generate_profile_report.py data/instruments_list_20250705_093603.csv

# With custom output name
python src/visualize/generate_profile_report.py data/instruments_list_20250705_093603.csv instrument_analysis
```

**Report Contents:**
- **📊 Overview**: Dataset summary and statistics
- **🔍 Variables**: Detailed analysis of each column
- **📈 Interactions**: Correlation between variables
- **⚠️ Missing Values**: Data quality analysis
- **📊 Distributions**: Histograms and charts
- **🔗 Correlations**: Heatmaps and relationships

## 🧪 Testing Instructions

### **1. Run All Tests**
```bash
# Run complete test suite
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src
```

### **2. Test Data Fetcher**
```bash
# Test instrument list fetching
python -m pytest tests/test_data_fetcher.py::test_fetch_instrument_list -v

# Test historical candles
python -m pytest tests/test_data_fetcher.py::test_fetch_historical_candles -v

# Test daily candles for instruments
python -m pytest tests/test_data_fetcher.py::test_fetch_daily_candles_for_instruments -v
```

### **3. Test Visualization Module**
```bash
# Test unified viewer (requires CSV file)
python src/visualize/unified_csv_viewer.py data/instruments_list_20250705_093603.csv --profile-only

# Test standalone profile generator
python src/visualize/generate_profile_report.py data/instruments_list_20250705_093603.csv
```

### **4. Test Pattern Analysis**
```bash
# Test candlestick pattern recognition
python -m pytest tests/test_candlestick_patterns.py -v

# Test one-off pattern analysis
python src/examples/example_oneoff_pattern_analysis.py
```

### **5. Test Examples**
```bash
# Set PYTHONPATH for examples
export PYTHONPATH=$(pwd)

# Test instrument list example
python src/examples/example_instrument_list.py

# Test daily candles example
python src/examples/example_daily_candles.py

# Test pattern analysis example
python src/examples/example_pattern_analysis.py
```

## 🚀 Quick Start Guide

### **1. Setup Environment**
```bash
# Clone and setup
git clone <repository-url>
cd candle-pattern-test
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Configure API Credentials**
Create `config/local-settings.json`:
```json
{
  "kite_connect": {
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "access_token": "your_access_token",
    "nifty_instrument_token": 256265
  },
  "logging": {
    "level": "INFO",
    "file": "logs/data_fetcher.log"
  }
}
```

### **3. Fetch Instrument Data**
```bash
# Fetch complete instrument list
python src/examples/example_instrument_list.py

# Fetch daily candles for configured instruments
python src/examples/example_daily_candles.py
```

### **4. Visualize Data**
```bash
# Start interactive viewer
python src/visualize/unified_csv_viewer.py data/instruments_list_20250705_093603.csv

# Access at http://127.0.0.1:5000
```

### **5. Run Pattern Analysis**
```bash
# Analyze patterns on NIFTY data
python src/examples/example_pattern_analysis.py

# One-off analysis on any CSV file
python src/examples/example_oneoff_pattern_analysis.py
```

## 📊 Example Outputs

### **CSV Files**
```
data/
├── instruments_list_20250705_093603.csv          # Complete instrument list
├── NIFTY_2025-05-29_to_2025-06-28_20250629_205543.csv
├── BANKNIFTY_2025-05-29_to_2025-06-28_20250629_205544.csv
├── RELIANCE_2025-05-29_to_2025-06-28_20250629_205547.csv
├── pattern_analysis_20250630_203801.csv          # Pattern analysis results
└── instruments_list_20250705_093603_profile.html # ydata-profiling report
```

### **Pattern Analysis Output**
```csv
date,open,high,low,close,volume,pattern
2025-06-28,19250.50,19300.25,19200.75,19275.30,1250000,"Doji,Spinning Top"
2025-06-27,19180.20,19250.80,19150.10,19220.45,1180000,"Hammer"
```

## 🔧 Configuration

### **Instrument List Configuration**
Edit `config/instrumentlist.json`:
```json
{
  "instruments": [
    { "name": "NIFTY", "description": "NIFTY 50 Index", "exchange": "NSE", "instrument_type": "EQ" },
    { "name": "BANKNIFTY", "description": "NIFTY Bank Index", "exchange": "NSE", "instrument_type": "EQ" },
    { "name": "INFY", "description": "Infosys Limited", "exchange": "NSE", "instrument_type": "EQ" },
    { "name": "RELIANCE", "description": "Reliance Industries Limited", "exchange": "NSE", "instrument_type": "EQ" }
  ],
  "default_settings": {
    "interval": "day",
    "save_csv": true,
    "date_format": "%Y-%m-%d"
  }
}
```

## 📝 Logging
All operations are logged to `logs/data_fetcher.log`:
- API calls and responses
- Token management events
- Data fetching operations
- Visualization generation
- Pattern analysis results
- Errors and warnings

## 🎯 Use Cases

### **1. Data Exploration**
- Use the interactive viewer to explore instrument data
- Filter by specific names (NIFTY, BANKNIFTY, etc.)
- Search for specific trading symbols
- Generate comprehensive data profiling reports

### **2. Pattern Analysis**
- Analyze candlestick patterns on historical data
- Run one-off analysis on any CSV file
- Export pattern results for further analysis

### **3. Research & Development**
- Test pattern recognition algorithms
- Validate data quality with profiling reports
- Explore correlations between variables
- Generate reproducible analysis workflows

## 🔍 Troubleshooting

### **Common Issues**

1. **Port 5000 Already in Use**
   ```bash
   # Use different port
   python src/visualize/unified_csv_viewer.py data/file.csv --port 8080
   ```

2. **ydata-profiling Import Error**
   ```bash
   # Install ydata-profiling
   pip install ydata-profiling
   ```

3. **API Authentication Issues**
   - Check `config/local-settings.json` credentials
   - Regenerate access token using `src/auth/token_generator.py`

4. **CSV File Not Found**
   - Ensure CSV file exists in `data/` directory
   - Check file permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆕 Recent Updates

### **v2.0 - Visualization Module**
- ✅ Added comprehensive CSV visualization tools
- ✅ Interactive Flask web interface with filtering
- ✅ ydata-profiling integration for automated analysis
- ✅ Unified viewer combining both approaches
- ✅ Enhanced pattern analysis with single-column output
- ✅ Improved project structure and organization
- ✅ Comprehensive testing and documentation

---

**Happy Trading! 📈📊** 