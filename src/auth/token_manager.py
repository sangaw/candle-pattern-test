"""
Token manager for Kite Connect API with automatic refresh logic.
"""
import json
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from kiteconnect import KiteConnect
from kiteconnect.exceptions import TokenException
import logging

logger = logging.getLogger(__name__)

class TokenManager:
    """
    Manages Kite Connect access tokens with automatic refresh capabilities.
    """
    
    def __init__(self, config_path: str = 'config/local-settings.json'):
        """
        Initialize the token manager.
        
        Args:
            config_path (str): Path to the configuration file
        """
        logger.info(f"Initializing TokenManager with config: {config_path}")
        self.config_path = config_path
        self.config = self._load_config()
        self.kite = None
        self.last_token_check = None
        self.token_validity_duration = timedelta(hours=23)  # Refresh before 24-hour expiry
        logger.info("TokenManager initialized successfully")
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            Dict: Configuration dictionary
        """
        logger.debug(f"Loading configuration from {self.config_path}")
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            logger.debug("Configuration loaded successfully")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file: {self.config_path}")
            raise ValueError(f"Invalid JSON in configuration file: {self.config_path}")
    
    def _save_config(self) -> bool:
        """
        Save configuration to file.
        
        Returns:
            bool: True if successful
        """
        logger.debug(f"Saving configuration to {self.config_path}")
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.debug("Configuration saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def _get_kite_config(self) -> Dict[str, Any]:
        """
        Get Kite Connect configuration.
        
        Returns:
            Dict: Kite Connect configuration
        """
        kite_config = self.config.get('kite_connect', {})
        logger.debug(f"Retrieved Kite config with API key: {kite_config.get('api_key', 'Not found')}")
        return kite_config
    
    def _update_access_token(self, access_token: str) -> bool:
        """
        Update access token in configuration.
        
        Args:
            access_token (str): New access token
            
        Returns:
            bool: True if successful
        """
        logger.info("Updating access token in configuration")
        try:
            self.config['kite_connect']['access_token'] = access_token
            success = self._save_config()
            if success:
                logger.info("Access token updated successfully")
            else:
                logger.error("Failed to save updated access token")
            return success
        except Exception as e:
            logger.error(f"Error updating access token: {str(e)}")
            return False
    
    def _is_token_expired(self) -> bool:
        """
        Check if the current token is expired or about to expire.
        
        Returns:
            bool: True if token is expired or will expire soon
        """
        if not self.last_token_check:
            logger.info("No previous token check found - token needs validation")
            return True
            
        # Check if we need to refresh (23 hours after last check)
        time_since_check = datetime.now() - self.last_token_check
        needs_refresh = time_since_check >= self.token_validity_duration
        
        if needs_refresh:
            logger.info(f"Token refresh needed. Time since last check: {time_since_check}")
        else:
            logger.debug(f"Token still valid. Time since last check: {time_since_check}")
            
        return needs_refresh
    
    def _validate_token(self) -> bool:
        """
        Validate the current access token by making a test API call.
        
        Returns:
            bool: True if token is valid
        """
        logger.info("Validating current access token")
        try:
            kite_config = self._get_kite_config()
            api_key = kite_config.get('api_key')
            access_token = kite_config.get('access_token')
            
            if not api_key or not access_token:
                logger.warning("API key or access token not found in configuration")
                return False
            
            logger.debug(f"Testing token with API key: {api_key[:8]}...")
            
            # Initialize Kite Connect
            kite = KiteConnect(api_key=api_key)
            kite.set_access_token(access_token)
            
            # Make a simple API call to test token
            profile = kite.profile()
            if profile:
                logger.info(f"Token validation successful for user: {profile.get('user_name', 'Unknown')}")
                return True
            else:
                logger.warning("Token validation failed - no profile returned")
                return False
                
        except TokenException as e:
            logger.warning(f"Token validation failed with TokenException: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            return False
    
    def get_valid_kite_instance(self) -> KiteConnect:
        """
        Get a valid Kite Connect instance with a working access token.
        
        Returns:
            KiteConnect: Valid Kite Connect instance
        """
        logger.info("Getting valid Kite Connect instance")
        
        # Check if we need to validate/refresh token
        if self._is_token_expired() or not self._validate_token():
            logger.info("Token needs refresh or validation - attempting refresh")
            refresh_success = self._refresh_token()
            if not refresh_success:
                logger.warning("Automatic token refresh failed - using current token")
        
        # Initialize and return Kite Connect instance
        kite_config = self._get_kite_config()
        api_key = kite_config.get('api_key')
        access_token = kite_config.get('access_token')
        
        if not api_key or not access_token:
            logger.error("API key or access token not found in configuration")
            raise ValueError("API key or access token not found in configuration")
        
        logger.debug("Initializing Kite Connect instance")
        self.kite = KiteConnect(api_key=api_key)
        self.kite.set_access_token(access_token)
        self.last_token_check = datetime.now()
        
        logger.info("Kite Connect instance ready with valid token")
        return self.kite
    
    def _refresh_token(self) -> bool:
        """
        Refresh the access token using the refresh token.
        
        Returns:
            bool: True if successful
        """
        logger.info("Attempting automatic token refresh")
        try:
            kite_config = self._get_kite_config()
            api_key = kite_config.get('api_key')
            refresh_token = kite_config.get('refresh_token')
            
            if not api_key or not refresh_token:
                logger.warning("API key or refresh token not found for automatic refresh")
                return False
            
            logger.debug("Using refresh token to renew access token")
            
            # Initialize Kite Connect
            kite = KiteConnect(api_key=api_key)
            
            # Renew session using refresh token
            data = kite.renew_access_token(refresh_token=refresh_token)
            new_access_token = data["access_token"]
            new_refresh_token = data.get("refresh_token", refresh_token)
            
            logger.info("Token refresh successful")
            
            # Update configuration
            self.config['kite_connect']['access_token'] = new_access_token
            if new_refresh_token != refresh_token:
                logger.info("New refresh token received - updating configuration")
                self.config['kite_connect']['refresh_token'] = new_refresh_token
            
            if self._save_config():
                logger.info("Refreshed tokens saved to configuration")
                return True
            else:
                logger.error("Failed to save refreshed tokens")
                return False
                
        except Exception as e:
            logger.error(f"Error during automatic token refresh: {str(e)}")
            return False
    
    def manual_token_refresh(self, request_token: str) -> bool:
        """
        Manually refresh token using a request token.
        This is used when automatic refresh fails.
        
        Args:
            request_token (str): Request token from Kite Connect login
            
        Returns:
            bool: True if successful
        """
        logger.info("Performing manual token refresh with request token")
        try:
            from .token_generator import generate_access_token
            
            kite_config = self._get_kite_config()
            api_key = kite_config.get('api_key')
            api_secret = kite_config.get('api_secret')
            
            if not api_key or not api_secret:
                logger.error("API key or secret not found for manual refresh")
                return False
            
            logger.debug("Generating new access token from request token")
            
            # Generate new access token
            new_access_token = generate_access_token(request_token, api_key, api_secret)
            
            if new_access_token:
                logger.info("Manual token refresh successful")
                return self._update_access_token(new_access_token)
            else:
                logger.error("Failed to generate new access token during manual refresh")
                return False
                
        except Exception as e:
            logger.error(f"Error during manual token refresh: {str(e)}")
            return False
    
    def get_token_info(self) -> Dict[str, Any]:
        """
        Get information about the current token status.
        
        Returns:
            Dict: Token information
        """
        logger.debug("Getting token information")
        kite_config = self._get_kite_config()
        
        info = {
            'api_key': kite_config.get('api_key'),
            'has_access_token': bool(kite_config.get('access_token')),
            'has_refresh_token': bool(kite_config.get('refresh_token')),
            'last_check': self.last_token_check.isoformat() if self.last_token_check else None,
            'needs_refresh': self._is_token_expired() if self.last_token_check else True
        }
        
        logger.debug(f"Token info: {info}")
        return info 