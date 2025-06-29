"""
Token generator for Kite Connect API.
"""
import json
import os
from kiteconnect import KiteConnect
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def load_kite_config() -> dict:
    """
    Load Kite Connect configuration from config file.
    """
    config_path = 'config/local-settings.json'
    logger.debug(f"Loading Kite Connect configuration from {config_path}")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            kite_config = config.get('kite_connect', {})
            logger.debug(f"Configuration loaded with API key: {kite_config.get('api_key', 'Not found')}")
            return kite_config
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in configuration file: {config_path}")
        raise ValueError(f"Invalid JSON in configuration file: {config_path}")

def generate_access_token(request_token: str, api_key: Optional[str] = None, api_secret: Optional[str] = None) -> Optional[str]:
    """
    Generate access token from request token.
    
    Args:
        request_token (str): The request token from Kite Connect login
        api_key (str, optional): API key. If not provided, loads from config
        api_secret (str, optional): API secret. If not provided, loads from config
        
    Returns:
        str: Access token if successful, None otherwise
    """
    logger.info("Starting access token generation process")
    logger.debug(f"Request token provided: {request_token[:8]}...")
    
    try:
        # Load config if not provided
        if not api_key or not api_secret:
            logger.debug("API key or secret not provided, loading from config")
            kite_config = load_kite_config()
            api_key = api_key or kite_config.get('api_key')
            api_secret = api_secret or kite_config.get('api_secret')
            
        if not api_key or not api_secret:
            logger.error("API key and secret must be provided or available in config")
            raise ValueError("API key and secret must be provided or available in config")
            
        logger.debug(f"Using API key: {api_key[:8]}...")
        logger.info("Initializing Kite Connect for token generation")
        
        # Generate session
        kite = KiteConnect(api_key=api_key)
        logger.debug("Making API call to generate session")
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]
        
        logger.info("Access token generated successfully")
        logger.debug(f"Generated access token: {access_token[:8]}...")
        return access_token
        
    except Exception as e:
        logger.error(f"Error generating access token: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        return None

def update_config_with_token(access_token: str) -> bool:
    """
    Update the configuration file with the new access token.
    
    Args:
        access_token (str): The new access token
        
    Returns:
        bool: True if successful, False otherwise
    """
    logger.info("Updating configuration file with new access token")
    try:
        config_path = 'config/local-settings.json'
        logger.debug(f"Reading current configuration from {config_path}")
        
        # Read current config
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update access token
        config['kite_connect']['access_token'] = access_token
        logger.debug("Access token updated in configuration object")
        
        # Write back to file
        logger.debug(f"Writing updated configuration to {config_path}")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
            
        logger.info("Configuration updated with new access token successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        return False

def main():
    """
    Command-line interface for token generation.
    """
    print("Kite Connect Access Token Generator")
    print("=" * 40)
    
    try:
        logger.info("Starting token generator CLI")
        kite_config = load_kite_config()
        print(f"API Key: {kite_config.get('api_key', 'Not found')}")
        print()
        
        # Get request token from user
        request_token = input("Enter your request token: ").strip()
        
        if not request_token:
            logger.warning("No request token provided by user")
            print("No request token provided.")
            return
            
        logger.info("Request token received, generating access token")
        
        # Generate access token
        access_token = generate_access_token(request_token)
        
        if access_token:
            print(f"\nAccess Token: {access_token}")
            logger.info("Access token generated successfully in CLI")
            
            # Ask if user wants to update config
            update_config = input("\nUpdate config/local-settings.json with this token? (y/n): ").strip().lower()
            
            if update_config == 'y':
                logger.info("User chose to update configuration")
                if update_config_with_token(access_token):
                    print("✓ Configuration updated successfully!")
                    logger.info("Configuration updated successfully via CLI")
                else:
                    print("✗ Failed to update configuration")
                    logger.error("Failed to update configuration via CLI")
            else:
                print("\nUpdate your config/local-settings.json manually with:")
                print(f'"access_token": "{access_token}"')
                logger.info("User chose manual configuration update")
        else:
            print("✗ Failed to generate access token")
            logger.error("Failed to generate access token in CLI")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        logger.error(f"Error in CLI: {str(e)}")

if __name__ == "__main__":
    main() 