# RITA Code Flow Documentation

This document provides a quick reference guide to all important code files in the candle-pattern-test project.

## Table of Contents
1. [Core Modules](#core-modules)
2. [Data Management](#data-management)
3. [Analysis & Visualization](#analysis--visualization)
4. [Workflow Scripts](#workflow-scripts)
5. [AI Agent Modules](#ai-agent-modules)
6. [Example Scripts](#example-scripts)

---

## Core Modules

### `src/data_fetcher.py`
**Purpose**: Fetches historical OHLC data from Kite Connect API  
**Key Features**:
- Automatic token management and refresh
- Fetches NIFTY price data for any date range
- Supports multiple time intervals (day, minute, 5minute, etc.)
- Fetches instrument lists and specific instrument data
- Logs all API calls and responses

**Main Classes**:
- `KiteConnectDataFetcher`: Handles all Kite Connect API interactions

**Key Methods**:
- `get_historical_data()`: Fetch daily NIFTY data
- `fetchHistoricalCandles()`: Fetch candles for specific instrument
- `fetchInstrumentList()`: Get complete instrument list
- `get_historical_data_for_instrument()`: Generic method for any instrument

---

### `src/candlestick_patterns.py`
**Purpose**: Analyzes and identifies candlestick patterns in OHLC data  
**Key Features**:
- Detects single candle patterns (Doji, Hammer, Shooting Star)
- Detects multi-candle patterns (Engulfing, Morning/Evening Star)
- Provides pattern summaries and date lookups
- Can process CSV files directly

**Main Classes**:
- `CandlestickPatternAnalyzer`: Pattern recognition engine

**Key Methods**:
- `analyze_patterns()`: Main pattern analysis
- `get_pattern_summary()`: Generate pattern counts
- `get_pattern_dates()`: Find dates when patterns occurred
- `process_csv_file()`: Process CSV files with pattern analysis

---

### `src/utils.py`
**Purpose**: Utility functions for candlestick analysis  
**Key Functions**:
- `is_bullish()` / `is_bearish()`: Check candle direction
- `is_doji()` / `is_hammer()` / `is_shooting_star()`: Pattern detection
- `calculate_body_size()` / `calculate_shadow_size()`: Size calculations
- `validate_ohlc_data()`: Data validation

---

### `src/auth/token_manager.py`
**Purpose**: Manages Kite Connect authentication tokens  
**Key Features**:
- Automatic token refresh before expiry
- Manual token refresh capability
- Token validation and status checking
- Secure configuration management

**Main Classes**:
- `TokenManager`: Authentication and token management

**Key Methods**:
- `get_valid_kite_instance()`: Returns valid Kite Connect instance
- `manual_token_refresh()`: Manual token refresh
- `get_token_info()`: Check token status

---

### `src/portfolio_manager.py`
**Purpose**: Manages portfolio operations via Kite Connect  
**Key Features**:
- Fetch holdings, positions, and margins
- Portfolio summary generation
- P&L calculations
- Logging and error handling

**Main Classes**:
- `PortfolioManager`: Portfolio management operations

**Key Methods**:
- `get_portfolio_holdings()`: Get current holdings
- `get_positions()`: Get day and net positions
- `get_margins()`: Get margin information
- `get_portfolio_summary()`: Comprehensive portfolio overview

---

## Data Management

### `src/workflow/nifty_feature_engineering.py` / `src/examples/example_feature_engineering.py`
**Purpose**: Feature engineering pipeline for NIFTY data  
**Key Features**:
- Merges multiple CSV files into single dataset
- Normalizes date formats with timezone handling
- Adds technical indicators (MA, RSI, MACD, Stochastic, etc.)
- Handles duplicate columns and date inconsistencies

**Key Functions**:
- `merge_csvs()`: Merge all CSVs in a directory
- `add_features()`: Add technical analysis features
- Main pipeline: Merge → Feature Engineering → Save

**Technical Indicators Added**:
- Daily return, log return, price range
- Moving averages (5-day, 20-day)
- Volatility (5-day, 20-day)
- RSI (14-period)
- MACD (12, 26, 9)
- Stochastic Oscillator (14)

---

## Analysis & Visualization

### `src/examples/cluster_overlay_price_chart.ipynb`
**Purpose**: Clusters market data and overlays on price charts  
**Features**:
- K-means clustering based on technical indicators
- Cluster statistics and analysis
- Visual price charts with cluster colors
- Consecutive cluster run analysis
- Market regime identification

**Key Operations**:
- Clustering by: daily_return, ma_5, ma_20, volatility, RSI, MACD, Stochastic
- Cluster descriptions: Uptrend/Profitable, Downtrend/High Volatility, Sideways/Low Volatility
- Regime definitions based on return and volatility quantiles

---

### `src/examples/eda_featured.ipynb`
**Purpose**: Exploratory Data Analysis of featured data  
**Features**:
- Statistical analysis of technical indicators
- Correlation matrices
- Distribution plots
- Feature importance analysis

---

### `src/examples/clustering_featured.ipynb`
**Purpose**: Advanced clustering analysis  
**Features**:
- Multiple clustering algorithms comparison
- Optimal cluster number selection
- Cluster interpretation and labeling
- Performance metrics

---

## Workflow Scripts

### `src/workflow/nifty_data_analysis.ipynb`
**Purpose**: End-to-end NIFTY data analysis workflow  
**Features**:
- Fetches data using Kite Connect
- Analyzes candlestick patterns
- Generates reports
- Creates visualizations

**Pipeline**:
1. Initialize components
2. Fetch historical data
3. Save as CSV
4. Analyze patterns
5. Generate report
6. Visualize results

---

### `src/workflow/nifty_data_analysis_25years.ipynb`
**Purpose**: Comprehensive 25-year NIFTY analysis  
**Scope**: Long-term historical analysis with trend analysis and pattern backtesting

---

## AI Agent Modules

### `src/ai_agent/tool_based_agent/tool_based_agent.py`
**Purpose**: AI agent that uses tools for market analysis  
**Features**:
- Natural language query processing
- Tool-based data fetching
- Automated analysis workflows
- Web chatbot interface

**Key Tools**:
- Data collection tools
- Instrument search tools
- Pattern analysis tools

---

### `src/ai_agent/base_agent/`
**Purpose**: Base agent framework with instrument discovery  
**Components**:
- `instrument_discovery.py`: Finds instruments by name
- `orchestrator.py`: Coordinates multiple agents
- `interactive_cli.py`: CLI interface
- `web_chatbot.py`: Web-based chat interface
- `launch_web_chatbot.py`: Launches web UI

---

## Example Scripts

### `src/examples/example_daily_candles.py`
**Purpose**: Fetch and analyze daily candle data  
**Features**:
- Fetches daily OHLC data
- Pattern detection
- CSV export
- Error handling

---

### `src/examples/example_historical_candles.py`
**Purpose**: Fetch historical candles for specific instruments  
**Features**:
- Multiple instruments support
- Date range selection
- Interval options
- Automatic CSV saving

---

### `src/examples/example_instrument_list.py`
**Purpose**: Fetch and search instruments  
**Features**:
- Fetch all instruments from Kite
- Search by symbol
- Filter by exchange
- Export to CSV

---

### `src/examples/example_pattern_analysis.py`
**Purpose**: Analyze candlestick patterns in CSV files  
**Features**:
- Load from CSV
- Pattern detection
- Summary generation
- Result export

---

### `src/examples/example_portfolio.py`
**Purpose**: Portfolio management examples  
**Features**:
- View holdings
- Check positions
- Margin analysis
- P&L tracking

---

### `src/examples/example_test_feature_engineering.py`
**Purpose**: Test feature engineering pipeline  
**Features**:
- Validates data merging
- Tests feature calculations
- Checks date normalization
- Validates technical indicators

---

### `src/examples/example_oneoff_pattern_analysis.py`
**Purpose**: One-time pattern analysis  
**Features**:
- Quick pattern checks
- Single-day analysis
- Direct API usage

---

## Model Files

### `src/model/RL-Nifty.py`
**Purpose**: Reinforcement Learning model for NIFTY trading  
**Features**:
- DQN agent implementation
- Training on historical data
- Strategy optimization

---

### `src/model/PINN.py`
**Purpose**: Physics-Informed Neural Network for market prediction  
**Features**:
- Incorporates market physics
- Prediction generation
- Trend forecasting

---

### `src/model/nifty-regression-model-dow-theory.ipynb`
**Purpose**: Dow Theory-based regression model  
**Features**:
- Trend identification
- Wave analysis
- Predictive modeling

---

## Visualization

### `src/visualize/`
**Purpose**: Data visualization and profiling  
**Files**:
- `generate_profile_report.py`: Generate pandas profiling reports
- `visualize_csv_profile.py`: CSV data visualization
- `unified_csv_viewer.py`: Unified CSV viewer with filtering
- `server.py`: Visualization web server

---

## Key Workflows

### Data Pipeline
1. **Fetch**: `data_fetcher.py` → Fetch from Kite Connect
2. **Merge**: `feature_engineering.py` → Merge CSVs
3. **Features**: `feature_engineering.py` → Add technical indicators
4. **Analyze**: `candlestick_patterns.py` → Pattern detection
5. **Cluster**: `cluster_overlay_price_chart.ipynb` → Clustering
6. **Visualize**: Jupyter notebooks → Charts and analysis

### Trading Pipeline
1. **Authentication**: `token_manager.py` → Get valid tokens
2. **Data**: `data_fetcher.py` → Fetch market data
3. **Analysis**: `candlestick_patterns.py` → Find patterns
4. **Portfolio**: `portfolio_manager.py` → Check holdings
5. **Trading**: AI agents or manual → Execute trades

---

## Configuration

### `config/local-settings.json`
**Purpose**: Configuration file for all modules  
**Contains**:
- Kite Connect credentials
- Token management settings
- Logging configuration
- Instrument tokens

---

## Important Notes

1. **Date Format**: All dates are standardized to `YYYY-MM-DD 00:00:00+05:30` format
2. **Token Management**: Automatic refresh every 23 hours
3. **Data Files**: Saved in `data/nifty/train/` directory
4. **Logs**: Stored in `logs/` directory
5. **Features**: Technical indicators require `ta` library installation

---

## Quick Reference

### Fetch NIFTY Data
```python
from data_fetcher import KiteConnectDataFetcher
fetcher = KiteConnectDataFetcher()
df = fetcher.get_historical_data('2025-01-01', '2025-12-31', 'day')
```

### Analyze Patterns
```python
from candlestick_patterns import CandlestickPatternAnalyzer
analyzer = CandlestickPatternAnalyzer()
result = analyzer.analyze_patterns(df)
```

### Feature Engineering
```python
# In Jupyter or via script
from src.examples.example_feature_engineering import *
merged_df = merge_csvs('data/nifty/train/', 'merged.csv')
featured_df = add_features(merged_df)
```

### Portfolio Operations
```python
from portfolio_manager import PortfolioManager
pm = PortfolioManager()
holdings = pm.get_portfolio_holdings()
summary = pm.get_portfolio_summary()
```

---

## File Structure Summary

```
candle-pattern-test/
├── src/
│   ├── data_fetcher.py          # Fetch data from Kite Connect
│   ├── candlestick_patterns.py  # Pattern analysis
│   ├── portfolio_manager.py     # Portfolio operations
│   ├── utils.py                 # Utility functions
│   ├── auth/                    # Authentication
│   ├── examples/                # Example scripts
│   ├── workflow/                # Workflow notebooks
│   ├── model/                    # ML models
│   └── visualize/               # Visualization tools
├── data/                        # Data files
├── config/                      # Configuration
└── logs/                        # Log files
```

---

*Last Updated: Generated automatically based on current codebase*


