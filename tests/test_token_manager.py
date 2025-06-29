import pytest
import json
from src.auth import TokenManager
from src.data_fetcher import KiteConnectDataFetcher

def test_token_manager_initialization():
    """Test TokenManager initialization."""
    token_manager = TokenManager()
    assert token_manager is not None
    assert token_manager.config is not None
    assert 'kite_connect' in token_manager.config

def test_get_token_info():
    """Test getting token information."""
    token_manager = TokenManager()
    token_info = token_manager.get_token_info()
    
    assert isinstance(token_info, dict)
    assert 'api_key' in token_info
    assert 'has_access_token' in token_info
    assert 'has_refresh_token' in token_info
    assert 'needs_refresh' in token_info

def test_data_fetcher_with_token_manager():
    """Test that data fetcher works with token manager."""
    fetcher = KiteConnectDataFetcher()
    
    # Test token info
    token_info = fetcher.get_token_info()
    assert isinstance(token_info, dict)
    assert token_info['has_access_token'] == True

@pytest.mark.skipif(
    not TokenManager().get_token_info()['has_access_token'],
    reason="No valid access token available"
)
def test_historical_data_with_token_manager():
    """Test historical data fetching with automatic token management."""
    fetcher = KiteConnectDataFetcher()
    
    # Use a valid historical date range
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