"""
Data fetching module for NIFTY price data using Kite Connect API.
"""
import os
import json
import pandas as pd
from datetime import datetime
from typing import Optional
import logging
from src.auth import TokenManager

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

    def fetchHistoricalCandles(self, instrument_token: int, from_datetime: str, to_datetime: str, interval: str = 'minute', save_csv: bool = True) -> pd.DataFrame:
        """
        Fetch historical candles using direct API endpoint with proper headers and optionally save as CSV.
        
        Args:
            instrument_token (int): Instrument token (e.g., 5633 for NSE-ACC)
            from_datetime (str): Start datetime in 'YYYY-MM-DD HH:MM:SS' format
            to_datetime (str): End datetime in 'YYYY-MM-DD HH:MM:SS' format
            interval (str): Candle interval (e.g., 'minute', '5minute', '15minute', '30minute', 'day')
            save_csv (bool): Whether to save the fetched data as a CSV file in the 'data' directory
        Returns:
            pd.DataFrame: DataFrame with columns ['date', 'open', 'high', 'low', 'close', 'volume']
        """
        logger.info(f"Fetching historical candles for instrument {instrument_token} from {from_datetime} to {to_datetime} with interval: {interval}")
        
        try:
            # Get a valid Kite Connect instance (with automatic token refresh)
            logger.debug("Getting valid Kite Connect instance with token management")
            kite = self.token_manager.get_valid_kite_instance()
            
            # Get current credentials
            kite_config = self.config.get('kite_connect', {})
            api_key = kite_config.get('api_key')
            access_token = kite_config.get('access_token')
            
            if not api_key or not access_token:
                logger.error("API key or access token not found in config")
                raise ValueError("API key or access token not found in config")
            
            # Format datetime strings for URL (replace spaces with +)
            from_formatted = from_datetime.replace(' ', '+')
            to_formatted = to_datetime.replace(' ', '+')
            
            # Construct the API URL
            base_url = "https://api.kite.trade"
            url = f"{base_url}/instruments/historical/{instrument_token}/{interval}"
            params = f"from={from_formatted}&to={to_formatted}"
            full_url = f"{url}?{params}"
            
            logger.debug(f"API URL: {full_url}")
            
            # Set up headers
            headers = {
                "X-Kite-Version": "3",
                "Authorization": f"token {api_key}:{access_token}"
            }
            
            logger.debug(f"Making direct API call with headers: {headers}")
            
            # Make the API call using requests (imported in kiteconnect)
            import requests
            response = requests.get(full_url, headers=headers)
            
            # Check response status
            if response.status_code != 200:
                logger.error(f"API call failed with status {response.status_code}: {response.text}")
                raise Exception(f"API call failed with status {response.status_code}")
            
            # Log response details for debugging
            logger.debug(f"Response content type: {response.headers.get('content-type', 'unknown')}")
            logger.debug(f"Response length: {len(response.content)} bytes")
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Log raw response for debugging
            if len(response.content) > 0:
                logger.debug(f"Raw response (first 1000 chars): {response.text[:1000]}")
            else:
                logger.warning("Empty response received")
                return pd.DataFrame()
            
            # Try to parse response as JSON
            try:
                data = response.json()
                logger.debug(f"Successfully parsed JSON response")
            except Exception as json_error:
                logger.error(f"Failed to parse JSON response: {json_error}")
                logger.debug(f"Response text (first 500 chars): {response.text[:500]}")
                raise Exception(f"Invalid JSON response: {json_error}")
            
            # Extract candles data
            candles = data.get('data', {}).get('candles', [])
            logger.info(f"Successfully fetched {len(candles)} candles")
            
            if not candles:
                logger.warning("No candles data returned")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(candles, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            
            # Convert date strings to datetime
            df['date'] = pd.to_datetime(df['date'])
            
            # Convert numeric columns
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            logger.info(f"Processed {len(df)} candles with date range: {df['date'].min()} to {df['date'].max()}")
            
            if not df.empty:
                logger.debug(f"Price range - Low: {df['low'].min():.2f}, High: {df['high'].max():.2f}")
                logger.debug(f"Volume range - Min: {df['volume'].min()}, Max: {df['volume'].max()}")
            
            # Save as CSV if requested
            if save_csv:
                os.makedirs('data', exist_ok=True)
                # Clean up file name
                from_str = df['date'].min().strftime('%Y%m%d_%H%M%S') if not df.empty else from_datetime.replace(':', '').replace(' ', '_')
                to_str = df['date'].max().strftime('%Y%m%d_%H%M%S') if not df.empty else to_datetime.replace(':', '').replace(' ', '_')
                filename = f"data/{instrument_token}_{interval}_{from_str}_to_{to_str}.csv"
                df.to_csv(filename, index=False)
                logger.info(f"Saved candles data to {filename}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical candles: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return pd.DataFrame()

    def fetchInstrumentList(self, save_csv: bool = True) -> pd.DataFrame:
        """
        Fetch the complete instrument list using Kite Connect library.
        
        Args:
            save_csv (bool): Whether to save the fetched data as a CSV file in the 'data' directory
            
        Returns:
            pd.DataFrame: DataFrame with instrument information including token, name, exchange, etc.
        """
        logger.info("Fetching complete instrument list from Kite Connect API")
        
        try:
            # Get a valid Kite Connect instance (with automatic token refresh)
            logger.debug("Getting valid Kite Connect instance with token management")
            kite = self.token_manager.get_valid_kite_instance()
            
            # Fetch instruments using Kite Connect library
            logger.info("Making API call to fetch instruments list")
            instruments = kite.instruments()
            
            logger.info(f"Successfully fetched {len(instruments)} instruments")
            
            if not instruments:
                logger.warning("No instruments data returned")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(instruments)
            
            # Log some statistics
            if not df.empty:
                logger.info(f"Processed {len(df)} instruments")
                logger.debug(f"Columns available: {list(df.columns)}")
                
                # Log exchange distribution if available
                if 'exchange' in df.columns:
                    exchange_counts = df['exchange'].value_counts()
                    logger.info(f"Exchange distribution: {dict(exchange_counts.head())}")
                
                # Log instrument type distribution if available
                if 'instrument_type' in df.columns:
                    type_counts = df['instrument_type'].value_counts()
                    logger.info(f"Instrument type distribution: {dict(type_counts.head())}")
            
            # Save as CSV if requested
            if save_csv:
                os.makedirs('data', exist_ok=True)
                # Create filename with timestamp
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"data/instruments_list_{timestamp}.csv"
                df.to_csv(filename, index=False)
                logger.info(f"Saved instruments list to {filename}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching instrument list: {str(e)}")
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