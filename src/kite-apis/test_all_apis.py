"""
Comprehensive test runner for all Kite Connect APIs.
This script executes all API endpoints and logs request/response data.
"""
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any

# Handle both relative and absolute imports
try:
    from .user_apis import UserAPIs
    from .orders_apis import OrdersAPIs
    from .portfolio_apis import PortfolioAPIs
    from .market_apis import MarketAPIs
    from .instruments_apis import InstrumentsAPIs
    from .historical_apis import HistoricalAPIs
    from .gtt_apis import GTTAPIs
    from .mutualfunds_apis import MutualFundsAPIs
except ImportError:
    # If running as script directly
    from user_apis import UserAPIs
    from orders_apis import OrdersAPIs
    from portfolio_apis import PortfolioAPIs
    from market_apis import MarketAPIs
    from instruments_apis import InstrumentsAPIs
    from historical_apis import HistoricalAPIs
    from gtt_apis import GTTAPIs
    from mutualfunds_apis import MutualFundsAPIs


class APITestRunner:
    """Test runner for all Kite Connect APIs."""
    
    def __init__(self):
        """Initialize the test runner."""
        self.logger = self._setup_logging()
        self.results = {}
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        import os
        os.makedirs('logs', exist_ok=True)
        
        logger = logging.getLogger('api_test_runner')
        logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler('logs/api_test_runner.log')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_section(self, title: str):
        """Log section header."""
        self.logger.info("\n" + "="*80)
        self.logger.info(f"TESTING: {title}")
        self.logger.info("="*80)
    
    def test_user_apis(self):
        """Test User APIs."""
        self.log_section("USER APIs")
        try:
            user_apis = UserAPIs()
            self.results['user_apis'] = user_apis.run_all_tests()
            self.logger.info("✓ User APIs completed")
        except Exception as e:
            self.logger.error(f"✗ User APIs failed: {str(e)}")
            self.results['user_apis'] = {'error': str(e)}
    
    def test_portfolio_apis(self):
        """Test Portfolio APIs."""
        self.log_section("PORTFOLIO APIs")
        try:
            portfolio_apis = PortfolioAPIs()
            self.results['portfolio_apis'] = portfolio_apis.run_all_tests()
            self.logger.info("✓ Portfolio APIs completed")
        except Exception as e:
            self.logger.error(f"✗ Portfolio APIs failed: {str(e)}")
            self.results['portfolio_apis'] = {'error': str(e)}
    
    def test_market_apis(self):
        """Test Market Data APIs."""
        self.log_section("MARKET DATA APIs")
        try:
            market_apis = MarketAPIs()
            self.results['market_apis'] = market_apis.run_all_tests()
            self.logger.info("✓ Market APIs completed")
        except Exception as e:
            self.logger.error(f"✗ Market APIs failed: {str(e)}")
            self.results['market_apis'] = {'error': str(e)}
    
    def test_instruments_apis(self):
        """Test Instruments APIs."""
        self.log_section("INSTRUMENTS APIs")
        try:
            instruments_apis = InstrumentsAPIs()
            self.results['instruments_apis'] = instruments_apis.run_all_tests()
            self.logger.info("✓ Instruments APIs completed")
        except Exception as e:
            self.logger.error(f"✗ Instruments APIs failed: {str(e)}")
            self.results['instruments_apis'] = {'error': str(e)}
    
    def test_historical_apis(self):
        """Test Historical Data APIs."""
        self.log_section("HISTORICAL DATA APIs")
        try:
            historical_apis = HistoricalAPIs()
            self.results['historical_apis'] = historical_apis.run_all_tests()
            self.logger.info("✓ Historical APIs completed")
        except Exception as e:
            self.logger.error(f"✗ Historical APIs failed: {str(e)}")
            self.results['historical_apis'] = {'error': str(e)}
    
    def test_gtt_apis(self):
        """Test GTT APIs."""
        self.log_section("GTT (Good Till Triggered) APIs")
        try:
            gtt_apis = GTTAPIs()
            self.results['gtt_apis'] = gtt_apis.run_all_tests()
            self.logger.info("✓ GTT APIs completed")
        except Exception as e:
            self.logger.error(f"✗ GTT APIs failed: {str(e)}")
            self.results['gtt_apis'] = {'error': str(e)}
    
    def test_orders_apis(self):
        """Test Orders APIs."""
        self.log_section("ORDERS APIs")
        try:
            orders_apis = OrdersAPIs()
            self.results['orders_apis'] = orders_apis.run_all_tests()
            self.logger.info("✓ Orders APIs completed")
        except Exception as e:
            self.logger.error(f"✗ Orders APIs failed: {str(e)}")
            self.results['orders_apis'] = {'error': str(e)}
    
    def test_mutualfunds_apis(self):
        """Test Mutual Funds APIs."""
        self.log_section("MUTUAL FUNDS APIs")
        try:
            mf_apis = MutualFundsAPIs()
            self.results['mutualfunds_apis'] = mf_apis.run_all_tests()
            self.logger.info("✓ Mutual Funds APIs completed")
        except Exception as e:
            self.logger.error(f"✗ Mutual Funds APIs failed: {str(e)}")
            self.results['mutualfunds_apis'] = {'error': str(e)}
    
    def save_results(self):
        """Save test results to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'logs/api_test_results_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        self.logger.info(f"\nResults saved to: {filename}")
    
    def print_summary(self):
        """Print test summary."""
        self.logger.info("\n" + "="*80)
        self.logger.info("TEST SUMMARY")
        self.logger.info("="*80)
        
        for api_category, results in self.results.items():
            status = "✓ PASS" if 'error' not in str(results) else "✗ FAIL"
            self.logger.info(f"{status}: {api_category.upper()}")
        
        self.logger.info("="*80)
    
    def run_all_tests(self):
        """Run all API tests."""
        self.logger.info("\n" + "="*80)
        self.logger.info("KITE CONNECT API TEST RUNNER")
        self.logger.info(f"Started at: {datetime.now()}")
        self.logger.info("="*80)
        
        # Run all tests
        self.test_user_apis()
        self.test_portfolio_apis()
        self.test_market_apis()
        self.test_instruments_apis()
        self.test_historical_apis()
        self.test_gtt_apis()
        self.test_orders_apis()
        self.test_mutualfunds_apis()
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
        
        self.logger.info(f"\nCompleted at: {datetime.now()}")


if __name__ == "__main__":
    runner = APITestRunner()
    runner.run_all_tests()

