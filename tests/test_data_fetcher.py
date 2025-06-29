import os
import json
import pytest
from src.data_fetcher import KiteConnectDataFetcher

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