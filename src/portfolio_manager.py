"""
Portfolio management module for Kite Connect API.
Handles portfolio holdings, positions, and margins.
"""
import os
import json
import pandas as pd
from datetime import datetime
import logging
from auth import TokenManager

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Configure logging
def setup_logging():
    """Setup logging configuration."""
    # Load configuration
    config_path = 'config/local-settings.json'
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Use default config if file not found
        config = {'logging': {'level': 'INFO', 'file': 'logs/portfolio_manager.log'}}
    
    # Configure logging
    log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO'))
    log_file = config.get('logging', {}).get('file', 'logs/portfolio_manager.log')
    
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

class PortfolioManager:
    """
    Manages portfolio operations using Kite Connect API with automatic token management.
    """
    
    def __init__(self, config_path: str = 'config/local-settings.json'):
        """
        Initialize the portfolio manager with token management.
        
        Args:
            config_path (str): Path to configuration file
        """
        logger.info(f"Initializing PortfolioManager with config: {config_path}")
        self.token_manager = TokenManager(config_path)
        self.config = self.token_manager.config
        logger.info("Portfolio manager initialized successfully")
        
    def get_portfolio_holdings(self) -> pd.DataFrame:
        """
        Fetch current portfolio holdings from Kite Connect API.
        
        Returns:
            pd.DataFrame: DataFrame with portfolio holdings information
        """
        logger.info("Fetching portfolio holdings from Kite Connect API")
        
        try:
            # Get a valid Kite Connect instance (with automatic token refresh)
            logger.debug("Getting valid Kite Connect instance with token management")
            kite = self.token_manager.get_valid_kite_instance()
            
            # Fetch portfolio holdings
            logger.info("Making API call to fetch portfolio holdings")
            holdings = kite.holdings()
            
            logger.info(f"Successfully fetched {len(holdings)} holdings")
            
            if not holdings:
                logger.warning("No holdings data returned")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(holdings)
            
            # Log some statistics
            if not df.empty:
                logger.info(f"Processed {len(df)} holdings")
                logger.debug(f"Columns available: {list(df.columns)}")
                
                # Calculate total portfolio value
                if 'last_price' in df.columns and 'quantity' in df.columns:
                    df['market_value'] = df['last_price'] * df['quantity']
                    total_value = df['market_value'].sum()
                    logger.info(f"Total portfolio value: ₹{total_value:,.2f}")
                
                # Log exchange distribution if available
                if 'exchange' in df.columns:
                    exchange_counts = df['exchange'].value_counts()
                    logger.info(f"Exchange distribution: {dict(exchange_counts)}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching portfolio holdings: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return pd.DataFrame()

    def get_positions(self) -> dict:
        """
        Fetch current positions (day and net) from Kite Connect API.
        
        Returns:
            dict: Dictionary with 'day' and 'net' positions
        """
        logger.info("Fetching positions from Kite Connect API")
        
        try:
            # Get a valid Kite Connect instance (with automatic token refresh)
            logger.debug("Getting valid Kite Connect instance with token management")
            kite = self.token_manager.get_valid_kite_instance()
            
            # Fetch positions
            logger.info("Making API call to fetch positions")
            positions = kite.positions()
            
            day_positions = positions.get('day', [])
            net_positions = positions.get('net', [])
            
            logger.info(f"Successfully fetched {len(day_positions)} day positions and {len(net_positions)} net positions")
            
            # Convert to DataFrames
            day_df = pd.DataFrame(day_positions) if day_positions else pd.DataFrame()
            net_df = pd.DataFrame(net_positions) if net_positions else pd.DataFrame()
            
            # Log statistics
            if not day_df.empty:
                logger.info(f"Day positions - {len(day_df)} positions")
                logger.debug(f"Day positions columns: {list(day_df.columns)}")
            
            if not net_df.empty:
                logger.info(f"Net positions - {len(net_df)} positions")
                logger.debug(f"Net positions columns: {list(net_df.columns)}")
            
            return {
                'day': day_df,
                'net': net_df
            }
            
        except Exception as e:
            logger.error(f"Error fetching positions: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return {'day': pd.DataFrame(), 'net': pd.DataFrame()}

    def get_margins(self) -> dict:
        """
        Fetch margin information from Kite Connect API.
        
        Returns:
            dict: Dictionary with margin information
        """
        logger.info("Fetching margin information from Kite Connect API")
        
        try:
            # Get a valid Kite Connect instance (with automatic token refresh)
            logger.debug("Getting valid Kite Connect instance with token management")
            kite = self.token_manager.get_valid_kite_instance()
            
            # Fetch margins
            logger.info("Making API call to fetch margin information")
            margins = kite.margins()
            
            logger.info("Successfully fetched margin information")
            logger.debug(f"Margin keys: {list(margins.keys())}")
            
            return margins
            
        except Exception as e:
            logger.error(f"Error fetching margin information: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return {}

    def get_portfolio_summary(self) -> dict:
        """
        Get a comprehensive portfolio summary including holdings, positions, and margins.
        
        Returns:
            dict: Dictionary with portfolio summary information
        """
        logger.info("Generating comprehensive portfolio summary")
        
        summary = {}
        
        try:
            # Fetch holdings
            holdings_df = self.get_portfolio_holdings()
            summary['holdings'] = holdings_df
            
            # Fetch positions
            positions = self.get_positions()
            summary['positions'] = positions
            
            # Fetch margins
            margins = self.get_margins()
            summary['margins'] = margins
            
            # Calculate portfolio statistics
            if not holdings_df.empty:
                portfolio_stats = {}
                
                if 'last_price' in holdings_df.columns and 'quantity' in holdings_df.columns:
                    holdings_df['market_value'] = holdings_df['last_price'] * holdings_df['quantity']
                    portfolio_stats['total_value'] = holdings_df['market_value'].sum()
                    portfolio_stats['total_quantity'] = holdings_df['quantity'].sum()
                    portfolio_stats['num_holdings'] = len(holdings_df)
                    
                    # Calculate P&L if available
                    if 'pnl' in holdings_df.columns:
                        portfolio_stats['total_pnl'] = holdings_df['pnl'].sum()
                    
                    logger.info(f"Portfolio Summary:")
                    logger.info(f"  - Total Holdings: {portfolio_stats['num_holdings']}")
                    logger.info(f"  - Total Value: ₹{portfolio_stats['total_value']:,.2f}")
                    logger.info(f"  - Total Quantity: {portfolio_stats['total_quantity']}")
                    if 'total_pnl' in portfolio_stats:
                        logger.info(f"  - Total P&L: ₹{portfolio_stats['total_pnl']:,.2f}")
                
                summary['portfolio_stats'] = portfolio_stats
            
            logger.info("Portfolio summary generated successfully")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating portfolio summary: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return summary

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