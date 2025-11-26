"""
Base client for Kite Connect API with authentication and logging.
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from kiteconnect import KiteConnect


class KiteAPIClient:
    """Base client for Kite Connect API with comprehensive logging."""
    
    def __init__(self, config_path: str = 'config/local-settings.json'):
        """
        Initialize the Kite API client.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config_path = self._resolve_config_path(config_path)
        self.config = self._load_config()
        self.logger = self._setup_logging()
        self.kite = None
        self.authenticate()
    
    def _resolve_config_path(self, config_path: str) -> str:
        """Resolve config path relative to project root."""
        # If path is absolute, use it as is
        if os.path.isabs(config_path):
            return config_path
        
        # If file exists at the given path, use it
        if os.path.exists(config_path):
            return os.path.abspath(config_path)
        
        # Otherwise, try to find it relative to project root
        # Project root is 2 levels up from this file (src/kite-apis/base_client.py)
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_file_dir))
        resolved_path = os.path.join(project_root, config_path)
        
        if os.path.exists(resolved_path):
            return resolved_path
        
        # If still not found, return original path (will fail with clear error)
        return config_path
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        with open(self.config_path, 'r') as f:
            return json.load(f)
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        # Resolve logs directory relative to project root
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_file_dir))
        logs_dir = os.path.join(project_root, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        logger = logging.getLogger('kite_api_client')
        logger.setLevel(logging.DEBUG)
        
        # Create file handler
        log_file_path = os.path.join(logs_dir, 'kite_api_client.log')
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def authenticate(self):
        """Authenticate with Kite Connect."""
        try:
            import sys
            import os
            # Add parent directory to path to import auth module
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
            from auth.token_manager import TokenManager
            
            self.logger.info("Initializing Kite Connect authentication")
            token_manager = TokenManager(self.config_path)
            self.kite = token_manager.get_valid_kite_instance()
            
            self.logger.info("Successfully authenticated with Kite Connect")
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise
    
    def log_request(self, method: str, endpoint: str, params: Optional[Dict] = None):
        """Log API request."""
        self.logger.info(f"REQUEST: {method} {endpoint}")
        if params:
            self.logger.debug(f"PARAMS: {json.dumps(params, indent=2)}")
    
    def log_response(self, data: Any, status: str = "SUCCESS"):
        """Log API response."""
        self.logger.info(f"RESPONSE STATUS: {status}")
        self.logger.debug(f"RESPONSE DATA: {json.dumps(data, indent=2, default=str)}")
        return data
    
    def log_error(self, error: Exception, context: str = ""):
        """Log error with context."""
        self.logger.error(f"ERROR in {context}: {str(error)}")
        self.logger.error(f"ERROR TYPE: {type(error).__name__}")


