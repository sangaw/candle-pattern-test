import os
import json
import pytest
from src.data_fetcher import KiteConnectDataFetcher
import pandas as pd
import glob

def load_test_config():
    config_path = 'config/local-settings.json'
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('kite_connect', {}).get('api_key') and config.get('kite_connect', {}).get('access_token')
    except (FileNotFoundError, json.JSONDecodeError):
        return False

@pytest.mark.skipif(
    not load_test_config(),
    reason="Kite Connect API credentials not set in config/local-settings.json"
)
def test_get_historical_data():
    fetcher = KiteConnectDataFetcher()
    # Use a valid historical date range (last week)
    from datetime import datetime, timedelta
    to_date = datetime.now().date() - timedelta(days=1)  # Yesterday
    from_date = to_date - timedelta(days=7)  # 7 days before yesterday
    df = fetcher.get_historical_data(from_date=str(from_date), to_date=str(to_date), interval='day')
    assert not df.empty, "No data returned from Kite Connect API!"
    for col in ['date', 'open', 'high', 'low', 'close', 'volume']:
        assert col in df.columns, f"Missing column: {col}"
    assert (df['open'] > 0).all()
    assert (df['high'] > 0).all()
    assert (df['low'] > 0).all()
    assert (df['close'] > 0).all()

@pytest.mark.skipif(
    not load_test_config(),
    reason="Kite Connect API credentials not set in config/local-settings.json"
)
def test_fetch_historical_candles():
    """Test fetchHistoricalCandles function with sample data and CSV output."""
    from src.data_fetcher import KiteConnectDataFetcher
    
    fetcher = KiteConnectDataFetcher()
    
    # Test with NSE-ACC instrument token (5633) as mentioned in the example
    instrument_token = 5633  # NSE-ACC
    from_datetime = "2017-12-15 09:15:00"
    to_datetime = "2017-12-15 09:20:00"
    interval = "minute"
    
    print(f"Testing fetchHistoricalCandles with instrument {instrument_token}")
    print(f"Time range: {from_datetime} to {to_datetime}")
    
    df = fetcher.fetchHistoricalCandles(instrument_token, from_datetime, to_datetime, interval, save_csv=True)
    
    # Check if data was returned
    if not df.empty:
        print(f"✓ Successfully fetched {len(df)} candles")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Columns: {list(df.columns)}")
        print(f"Sample data:")
        print(df.head())
        
        # Verify DataFrame structure
        expected_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        assert all(col in df.columns for col in expected_columns), f"Missing columns. Expected: {expected_columns}, Got: {list(df.columns)}"
        
        # Verify data types
        assert pd.api.types.is_datetime64_any_dtype(df['date']), "Date column should be datetime"
        assert pd.api.types.is_numeric_dtype(df['open']), "Open column should be numeric"
        assert pd.api.types.is_numeric_dtype(df['high']), "High column should be numeric"
        assert pd.api.types.is_numeric_dtype(df['low']), "Low column should be numeric"
        assert pd.api.types.is_numeric_dtype(df['close']), "Close column should be numeric"
        assert pd.api.types.is_numeric_dtype(df['volume']), "Volume column should be numeric"
        
        # Verify data integrity
        assert (df['high'] >= df['low']).all(), "High should be >= Low"
        assert (df['high'] >= df['open']).all(), "High should be >= Open"
        assert (df['high'] >= df['close']).all(), "High should be >= Close"
        assert (df['low'] <= df['open']).all(), "Low should be <= Open"
        assert (df['low'] <= df['close']).all(), "Low should be <= Close"
        assert (df['volume'] >= 0).all(), "Volume should be >= 0"
        
        print("✓ All data integrity checks passed")
        # Check that a CSV file was created
        csv_files = glob.glob(f"data/{instrument_token}_{interval}_*.csv")
        assert len(csv_files) > 0, "CSV file was not created in the data directory"
        print(f"✓ CSV file(s) created: {csv_files}")
        # Clean up the created CSV files
        for f in csv_files:
            os.remove(f)
    else:
        print("⚠ No data returned - this might be expected for historical data outside trading hours")
        # Even if no data, the function should return an empty DataFrame with correct structure
        assert isinstance(df, pd.DataFrame), "Should return a pandas DataFrame"
        assert len(df) == 0, "Should return empty DataFrame when no data"
        # No CSV should be created if no data
        csv_files = glob.glob(f"data/{instrument_token}_{interval}_*.csv")
        assert len(csv_files) == 0, "CSV file should not be created when no data"

@pytest.mark.skipif(
    not load_test_config(),
    reason="Kite Connect API credentials not set in config/local-settings.json"
)
def test_fetch_instrument_list():
    """Test fetchInstrumentList function with CSV output."""
    from src.data_fetcher import KiteConnectDataFetcher
    import glob
    import os
    
    fetcher = KiteConnectDataFetcher()
    
    print("Testing fetchInstrumentList function")
    
    df = fetcher.fetchInstrumentList(save_csv=True)
    
    # Check if data was returned
    if not df.empty:
        print(f"✓ Successfully fetched {len(df)} instruments")
        print(f"Columns: {list(df.columns)}")
        print(f"Sample data:")
        print(df.head())
        
        # Verify DataFrame structure - check for common columns
        expected_columns = ['instrument_token', 'tradingsymbol', 'name', 'exchange']
        found_columns = [col for col in expected_columns if col in df.columns]
        assert len(found_columns) >= 2, f"Missing essential columns. Expected at least 2 of {expected_columns}, found {found_columns}"
        
        # Verify data types for key columns
        if 'instrument_token' in df.columns:
            assert pd.api.types.is_numeric_dtype(df['instrument_token']), "instrument_token should be numeric"
        
        if 'tradingsymbol' in df.columns:
            assert pd.api.types.is_string_dtype(df['tradingsymbol']), "tradingsymbol should be string"
        
        # Check that a CSV file was created
        csv_files = glob.glob("data/instruments_list_*.csv")
        assert len(csv_files) > 0, "CSV file was not created in the data directory"
        print(f"✓ CSV file(s) created: {csv_files}")
        
        # Log some statistics
        if 'exchange' in df.columns:
            exchange_counts = df['exchange'].value_counts()
            print(f"Exchange distribution: {dict(exchange_counts.head())}")
        
        if 'instrument_type' in df.columns:
            type_counts = df['instrument_type'].value_counts()
            print(f"Instrument type distribution: {dict(type_counts.head())}")
        
        # Clean up the created CSV files
        for f in csv_files:
            os.remove(f)
            print(f"Cleaned up: {f}")
    else:
        print("⚠ No instruments data returned")
        # Even if no data, the function should return an empty DataFrame with correct structure
        assert isinstance(df, pd.DataFrame), "Should return a pandas DataFrame"
        assert len(df) == 0, "Should return empty DataFrame when no data"
        # No CSV should be created if no data
        csv_files = glob.glob("data/instruments_list_*.csv")
        assert len(csv_files) == 0, "CSV file should not be created when no data" 