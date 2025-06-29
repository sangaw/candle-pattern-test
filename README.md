# NIFTY Candlestick Pattern Tester

This project analyzes NIFTY and other instrument candlestick patterns using the Kite Connect API. It supports robust data fetching, token management, SHA-256 hashing, CSV export, and comprehensive examples and tests for NIFTY candlestick pattern analysis.

## Features
- Fetch historical OHLC (Open, High, Low, Close) data for NIFTY and any instrument on Kite Connect
- Automatic token management and refresh for Kite Connect API
- SHA-256 hash generation for secure API authentication
- Save fetched data as CSV files in the `data/` folder
- Fetch and export the complete instrument list from Kite Connect
- Fetch daily candles for a configurable list of instruments
- Detailed logging to `logs/data_fetcher.log`
- Example scripts for all major features
- Comprehensive tests

## Project Structure
```
candle-pattern-test/
├── config/
│   └── instrumentlist.json   # List of instruments to fetch daily candles for
├── data/                    # All fetched CSV data is saved here
├── logs/
│   └── data_fetcher.log     # Log file for all data fetching operations
├── src/
│   ├── auth/                # Token management and authentication
│   ├── examples/            # Example scripts
│   ├── candlestick_patterns.py
│   ├── data_fetcher.py      # Main data fetching logic
│   └── utils.py
├── tests/                   # Test suite
├── requirements.txt
└── README.md
```

## Configuration

### Instrument List
Edit `config/instrumentlist.json` to specify which instruments to fetch daily candles for. Example:
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

### API Credentials
Set up your Kite Connect API credentials in `config/local-settings.json` as described in the earlier sections.

## Usage

### Fetch Daily Candles for Configured Instruments
Run the example script:
```bash
python -m src.examples.example_daily_candles
```
This will fetch daily candles for all instruments listed in `config/instrumentlist.json` for the last 30 days and save them as CSV files in the `data/` folder. The script prints a summary for each instrument.

### Fetch Complete Instrument List
Run:
```bash
python -m src.examples.example_instrument_list
```

### Logging
All data fetching operations are logged to `logs/data_fetcher.log`. The log includes:
- API calls and responses
- Token management events
- Errors and warnings
- File save operations

## Tests
Run all tests with:
```bash
pytest
```

## Example Output
CSV files are saved in the `data/` folder with names like:
```
NIFTY_2025-05-29_to_2025-06-28_20250629_205543.csv
BANKNIFTY_2025-05-29_to_2025-06-28_20250629_205544.csv
RELIANCE_2025-05-29_to_2025-06-28_20250629_205547.csv
```

## Notes
- If an instrument is not found, check the exact trading symbol in the instrument list (e.g., "INFY" for Infosys).
- The project is designed for extensibility—add more instruments or features as needed!

## Project Overview

This project helps in:
- Fetching NIFTY historical and intraday price data (Open, High, Low, Close, Volume) using Kite Connect API
- Identifying various candlestick patterns
- Testing pattern recognition algorithms
- Analyzing pattern effectiveness
- **Automatic token management** with refresh capabilities
- **SHA-256 hash generation** for API authentication
- **CSV data export** for fetched historical candles

## Project Structure

```
candle-pattern-test/
├── src/                    # Source code package
│   ├── __init__.py
│   ├── data_fetcher.py    # NIFTY data fetching module (Kite Connect)
│   ├── candlestick_patterns.py  # Pattern recognition logic
│   ├── utils.py           # Utility functions
│   ├── auth/              # Authentication module
│   │   ├── __init__.py
│   │   ├── token_manager.py    # Automatic token management
│   │   └── token_generator.py  # Token generation & SHA-256 utilities
│   └── examples/          # Example scripts
│       ├── __init__.py
│       ├── example_historical_candles.py  # Example for historical candles
│       ├── example_sha256.py     # Example for SHA-256 hash generation
│       └── example_instrument_list.py  # Example for instrument list
├── tests/                 # Test package
│   ├── __init__.py
│   ├── test_data_fetcher.py
│   ├── test_token_manager.py
│   ├── test_candlestick_patterns.py
│   └── test_utils.py
├── config/                # Configuration directory
│   └── local-settings.json  # Kite Connect API configuration
├── data/                  # CSV data files directory
├── logs/                  # Log files directory
├── requirements.txt       # Python dependencies
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Features

- **Data Fetching**: Retrieve NIFTY historical and intraday OHLCV data (via Kite Connect)
- **Historical Candles API**: Direct API endpoint access with proper headers
- **Instrument List**: Fetch complete instrument list with tokens and metadata
- **CSV Data Export**: Automatically save fetched data as CSV files
- **SHA-256 Hash Generation**: Generate hashes for API authentication
- **Pattern Recognition**: Identify common candlestick patterns
- **Testing Framework**: Comprehensive unit tests
- **Extensible**: Easy to add new patterns and data sources
- **Automatic Token Management**: Handles token refresh and validation automatically

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd candle-pattern-test
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your Kite Connect API credentials:

### Getting Kite Connect API Credentials

1. **Create a Kite Connect App**:
   - Go to [Kite Connect Developer Console](https://developers.kite.trade/)
   - Sign up/login with your Zerodha account
   - Create a new app to get your API key

2. **Get Access Token**:
   - Replace `XXX` in the URL below with your actual API key:
     ```
     https://kite.zerodha.com/connect/login?api_key=XXX
     ```
   - Open this URL in your browser
   - Login with your Zerodha credentials
   - After successful login, you'll be redirected to your redirect URL with a `request_token` parameter
   - Copy the `request_token` value from the URL

3. **Generate Access Token**:
   - Use the token generator utility:
   ```bash
   python src/auth/token_generator.py
   ```
   - Or use the Kite Connect Python library:
   ```python
   from src.auth import generate_access_token
   
   access_token = generate_access_token("your_request_token")
   ```

4. **Update Configuration**:
   - Edit `config/local-settings.json` and replace the placeholder values:
   ```json
   {
     "kite_connect": {
       "api_key": "your_kite_api_key_here",
       "api_secret": "your_api_secret_here",
       "access_token": "your_access_token_here",
       "refresh_token": "",
       "nifty_instrument_token": 256265
     },
     "logging": {
       "level": "INFO",
       "file": "logs/data_fetcher.log"
     }
   }
   ```

**Note**: The system now includes automatic token management. Access tokens will be automatically validated and refreshed when needed.

## Usage

### Basic Usage

```python
from src.data_fetcher import KiteConnectDataFetcher
from src.candlestick_patterns import CandlestickPatternAnalyzer

# Fetch NIFTY historical data (with automatic token management)
fetcher = KiteConnectDataFetcher()
data = fetcher.get_historical_data(from_date="2024-01-01", to_date="2024-01-31", interval="day")

# Analyze patterns
analyzer = CandlestickPatternAnalyzer()
patterns = analyzer.analyze_patterns(data)

print(patterns)
```

### Instrument List

```python
from src.data_fetcher import KiteConnectDataFetcher

fetcher = KiteConnectDataFetcher()

# Fetch complete instrument list
df = fetcher.fetchInstrumentList(save_csv=True)

print(f"Fetched {len(df)} instruments")
print(f"Exchanges: {df['exchange'].value_counts().to_dict()}")
print(f"Instrument types: {df['instrument_type'].value_counts().to_dict()}")

# Search for specific instruments
nifty_instruments = df[df['tradingsymbol'].str.contains('NIFTY', case=False)]
print(f"NIFTY instruments: {len(nifty_instruments)}")
```

### Historical Candles with CSV Export

```python
from src.data_fetcher import KiteConnectDataFetcher

fetcher = KiteConnectDataFetcher()

# Fetch minute candles for NSE-ACC (example from Kite Connect docs)
instrument_token = 5633  # NSE-ACC
from_datetime = "2017-12-15 09:15:00"
to_datetime = "2017-12-15 09:20:00"
interval = "minute"

# This will fetch data and save as CSV in the data/ folder
df = fetcher.fetchHistoricalCandles(
    instrument_token=instrument_token,
    from_datetime=from_datetime,
    to_datetime=to_datetime,
    interval=interval,
    save_csv=True  # Automatically saves to data/ folder
)

print(f"Fetched {len(df)} candles")
print(f"CSV file saved in data/ folder")
```

### SHA-256 Hash Generation

```python
from src.auth.token_generator import generate_sha256_hash, generate_sha256_hash_from_config

# Generate hash with explicit values
api_key = "your_api_key"
request_token = "your_request_token"
api_secret = "your_api_secret"

hash_result = generate_sha256_hash(api_key, request_token, api_secret)
print(f"SHA-256 Hash: {hash_result}")

# Generate hash using config file credentials
hash_from_config = generate_sha256_hash_from_config(request_token)
print(f"SHA-256 Hash from config: {hash_from_config}")
```

### Token Management

```python
from src.auth import TokenManager

# Check token status
token_manager = TokenManager()
token_info = token_manager.get_token_info()
print(f"Token needs refresh: {token_info['needs_refresh']}")

# Manual token refresh (if needed)
success = token_manager.manual_token_refresh("your_request_token")
```

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_token_manager.py

# Run with coverage
python -m pytest tests/ --cov=src
```

### Example Scripts

```bash
# Run historical candles example
python -m src.examples.example_historical_candles

# Run SHA-256 hash example
python -m src.examples.example_sha256

# Run instrument list example
python -m src.examples.example_instrument_list

# Run token generator with menu options
python src/auth/token_generator.py
```

## API Endpoints

### Historical Candles API

The project supports the direct Kite Connect historical candles API endpoint:

```
GET https://api.kite.trade/instruments/historical/{instrument_token}/{interval}?from={from_datetime}&to={to_datetime}
```

Headers:
- `X-Kite-Version: 3`
- `Authorization: token {api_key}:{access_token}`

Example:
```bash
curl "https://api.kite.trade/instruments/historical/5633/minute?from=2017-12-15+09:15:00&to=2017-12-15+09:20:00" \
    -H "X-Kite-Version: 3" \
    -H "Authorization: token api_key:access_token"
```

## Candlestick Patterns Supported

- **Doji**: Open and close prices are nearly equal
- **Hammer**: Small body with long lower shadow
- **Shooting Star**: Small body with long upper shadow
- **Engulfing**: Bullish and Bearish engulfing patterns
- **Morning Star**: Three-candle bullish reversal pattern
- **Evening Star**: Three-candle bearish reversal pattern

## Data Files

CSV files are automatically generated in the `data/` folder with the naming convention:
```
{instrument_token}_{interval}_{from_datetime}_to_{to_datetime}.csv
```

Example: `5633_minute_20171215_091500_to_20171215_092000.csv`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This project is for educational and research purposes only. It should not be used as financial advice. Always do your own research before making investment decisions. 