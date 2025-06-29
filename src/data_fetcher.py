"""
Data fetching module for NIFTY price data using Kite Connect API.
"""
import os
import json
import pandas as pd
from datetime import datetime
from typing import Optional
import logging
from .auth import TokenManager

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging first, before any logger calls
def setup_logging():
    """Setup logging configuration."""
    # Load configuration
    config_path = 'config/local-settings.json'
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Use default config if file not found
        config = {'logging': {'level': 'INFO', 'file': 'logs/data_fetcher.log'}}
    
    # Configure logging
    log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO'))
    log_file = config.get('logging', {}).get('file', 'logs/data_fetcher.log')
    
    # Clear any existing handlers
    logging.getLogger().handlers.clear()
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ],
        force=True  # Force reconfiguration
    )

# Setup logging immediately
setup_logging()
logger = logging.getLogger(__name__)

# Load configuration from local-settings.json
def load_config():
    config_path = 'config/local-settings.json'
    logger.debug(f"Loading configuration from {config_path}")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.debug("Configuration loaded successfully")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file: {config_path}")
        raise ValueError(f"Invalid JSON in configuration file: {config_path}")

config = load_config()

class KiteConnectDataFetcher:
    """
    Fetches NIFTY OHLC data using Kite Connect API with automatic token management.
    """
    
    def __init__(self, config_path: str = 'config/local-settings.json'):
        """
        Initialize the data fetcher with token management.
        
        Args:
            config_path (str): Path to configuration file
        """
        logger.info(f"Initializing KiteConnectDataFetcher with config: {config_path}")
        self.token_manager = TokenManager(config_path)
        self.config = self.token_manager.config
        kite_config = self.config.get('kite_connect', {})
        self.nifty_token = kite_config.get('nifty_instrument_token', 256265)
        logger.info(f"Data fetcher initialized with NIFTY token: {self.nifty_token}")
        
    def get_historical_data(self, from_date: str, to_date: str, interval: str = 'day') -> pd.DataFrame:
        """
        Fetch historical OHLC data for NIFTY with automatic token refresh.
        
        Args:
            from_date (str): Start date in 'YYYY-MM-DD' format
            to_date (str): End date in 'YYYY-MM-DD' format
            interval (str): Candle interval (e.g., 'day', 'minute', '5minute')
            
        Returns:
            pd.DataFrame: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
        """
        logger.info(f"Fetching historical data for NIFTY from {from_date} to {to_date} with interval: {interval}")
        
        try:
            # Get a valid Kite Connect instance (with automatic token refresh)
            logger.debug("Getting valid Kite Connect instance with token management")
            kite = self.token_manager.get_valid_kite_instance()
            
            # Parse dates
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            logger.debug(f"Parsed dates - From: {from_dt}, To: {to_dt}")
            
            # Fetch historical data
            logger.info(f"Making API call to fetch {interval} candles for NIFTY")
            data = kite.historical_data(
                instrument_token=self.nifty_token,
                from_date=from_dt,
                to_date=to_dt,
                interval=interval
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            logger.info(f"Successfully fetched {len(df)} candles for NIFTY from {from_date} to {to_date}")
            
            if not df.empty:
                logger.debug(f"Data sample - Date range: {df['date'].min()} to {df['date'].max()}")
                logger.debug(f"Price range - Low: {df['low'].min():.2f}, High: {df['high'].max():.2f}")
                logger.debug(f"Volume range - Min: {df['volume'].min()}, Max: {df['volume'].max()}")
            else:
                logger.warning("No data returned from API call")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return pd.DataFrame()
    
    def get_token_info(self) -> dict:
        """
        Get information about the current token status.
        
        Returns:
            dict: Token information
        """
        logger.debug("Getting token information from token manager")
        token_info = self.token_manager.get_token_info()
        logger.info(f"Token status - Has access token: {token_info['has_access_token']}, Needs refresh: {token_info['needs_refresh']}")
        return token_info
    
    def manual_token_refresh(self, request_token: str) -> bool:
        """
        Manually refresh the access token using a request token.
        
        Args:
            request_token (str): Request token from Kite Connect login
            
        Returns:
            bool: True if successful
        """
        logger.info("Initiating manual token refresh")
        success = self.token_manager.manual_token_refresh(request_token)
        if success:
            logger.info("Manual token refresh completed successfully")
        else:
            logger.error("Manual token refresh failed")
        return success

    def get_day_data_and_log_pattern(self, date: str, analyzer=None) -> Optional[dict]:
        """
        Fetch NIFTY OHLC data for a specific day and log the candlestick pattern.
        Args:
            date (str): Date in 'YYYY-MM-DD' format
            analyzer: CandlestickPatternAnalyzer instance (optional)
        Returns:
            dict: OHLC data for the day, or None if not found
        """
        logger.info(f"Fetching NIFTY OHLC data for {date}")
        df = self.get_historical_data(from_date=date, to_date=date, interval='day')
        if df.empty:
            logger.warning(f"No data found for NIFTY on {date}")
            return None
        day_row = df.iloc[0].to_dict()
        logger.info(f"NIFTY OHLC on {date}: {day_row}")
        if analyzer:
            logger.info(f"Analyzing candlestick pattern for {date}")
            # Rename columns to capitalized format for analyzer compatibility
            df_renamed = df.rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'
            })
            result = analyzer.analyze_patterns(df_renamed)
            pattern_info = result.iloc[0].to_dict()
            # Find which pattern is True
            patterns = [k for k, v in pattern_info.items() if k.startswith('is_') and v]
            if patterns:
                logger.info(f"Candlestick pattern(s) on {date}: {patterns}")
            else:
                logger.info(f"No major candlestick pattern detected on {date}")
        return day_row 