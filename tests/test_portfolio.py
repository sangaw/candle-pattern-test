#!/usr/bin/env python3
"""
Tests for portfolio functionality.
"""
import pytest
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from portfolio_manager import PortfolioManager

def load_test_config():
    """Load test configuration to check if API credentials are available."""
    try:
        import json
        with open('config/local-settings.json', 'r') as f:
            config = json.load(f)
        kite_config = config.get('kite_connect', {})
        return bool(kite_config.get('api_key') and kite_config.get('access_token'))
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return False

@pytest.mark.skipif(
    not load_test_config(),
    reason="Kite Connect API credentials not set in config/local-settings.json"
)
def test_get_portfolio_holdings():
    """Test get_portfolio_holdings function."""
    portfolio_manager = PortfolioManager()
    holdings_df = portfolio_manager.get_portfolio_holdings()
    
    # Check if we got a DataFrame (even if empty)
    assert isinstance(holdings_df, pd.DataFrame), "Should return a pandas DataFrame"
    
    if not holdings_df.empty:
        print(f"✓ Successfully fetched {len(holdings_df)} holdings")
        print(f"Columns: {list(holdings_df.columns)}")
        
        # Check for expected columns
        expected_columns = ['tradingsymbol', 'quantity', 'last_price']
        found_columns = [col for col in expected_columns if col in holdings_df.columns]
        assert len(found_columns) >= 2, f"Should have at least 2 of {expected_columns}, found {found_columns}"
        
        # Check data types
        if 'quantity' in holdings_df.columns:
            assert pd.api.types.is_numeric_dtype(holdings_df['quantity']), "Quantity should be numeric"
        if 'last_price' in holdings_df.columns:
            assert pd.api.types.is_numeric_dtype(holdings_df['last_price']), "Last price should be numeric"
        
        # Check for market_value column (added by our function)
        if 'market_value' in holdings_df.columns:
            assert pd.api.types.is_numeric_dtype(holdings_df['market_value']), "Market value should be numeric"
            assert (holdings_df['market_value'] >= 0).all(), "Market value should be non-negative"
    else:
        print("⚠ No holdings found (this might be expected if account has no holdings)")

@pytest.mark.skipif(
    not load_test_config(),
    reason="Kite Connect API credentials not set in config/local-settings.json"
)
def test_get_positions():
    """Test get_positions function."""
    portfolio_manager = PortfolioManager()
    positions = portfolio_manager.get_positions()
    
    # Check structure
    assert isinstance(positions, dict), "Should return a dictionary"
    assert 'day' in positions, "Should have 'day' key"
    assert 'net' in positions, "Should have 'net' key"
    
    day_positions = positions['day']
    net_positions = positions['net']
    
    assert isinstance(day_positions, pd.DataFrame), "Day positions should be a DataFrame"
    assert isinstance(net_positions, pd.DataFrame), "Net positions should be a DataFrame"
    
    if not day_positions.empty:
        print(f"✓ Day positions: {len(day_positions)} positions")
        print(f"Day position columns: {list(day_positions.columns)}")
    
    if not net_positions.empty:
        print(f"✓ Net positions: {len(net_positions)} positions")
        print(f"Net position columns: {list(net_positions.columns)}")

@pytest.mark.skipif(
    not load_test_config(),
    reason="Kite Connect API credentials not set in config/local-settings.json"
)
def test_get_margins():
    """Test get_margins function."""
    portfolio_manager = PortfolioManager()
    margins = portfolio_manager.get_margins()
    
    # Check if we got a dictionary
    assert isinstance(margins, dict), "Should return a dictionary"
    
    if margins:
        print(f"✓ Margin information fetched")
        print(f"Available margin keys: {list(margins.keys())}")
        
        # Check for common margin keys
        common_keys = ['equity', 'commodity', 'currency']
        found_keys = [key for key in common_keys if key in margins]
        print(f"Found margin types: {found_keys}")
    else:
        print("⚠ No margin information available")

@pytest.mark.skipif(
    not load_test_config(),
    reason="Kite Connect API credentials not set in config/local-settings.json"
)
def test_get_portfolio_summary():
    """Test get_portfolio_summary function."""
    portfolio_manager = PortfolioManager()
    summary = portfolio_manager.get_portfolio_summary()
    
    # Check structure
    assert isinstance(summary, dict), "Should return a dictionary"
    assert 'holdings' in summary, "Should have 'holdings' key"
    assert 'positions' in summary, "Should have 'positions' key"
    assert 'margins' in summary, "Should have 'margins' key"
    
    holdings_df = summary['holdings']
    positions = summary['positions']
    margins = summary['margins']
    
    assert isinstance(holdings_df, pd.DataFrame), "Holdings should be a DataFrame"
    assert isinstance(positions, dict), "Positions should be a dictionary"
    assert isinstance(margins, dict), "Margins should be a dictionary"
    
    # Check portfolio stats if available
    if 'portfolio_stats' in summary:
        stats = summary['portfolio_stats']
        print("Portfolio Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Check for expected stats
        expected_stats = ['num_holdings', 'total_value', 'total_quantity']
        found_stats = [stat for stat in expected_stats if stat in stats]
        print(f"Found statistics: {found_stats}")
    else:
        print("⚠ No portfolio statistics available")

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 