"""
Market data API client for Kite Connect.
"""
try:
    from .base_client import KiteAPIClient
except ImportError:
    from base_client import KiteAPIClient
from typing import List


class MarketAPIs(KiteAPIClient):
    """APIs for market quotes and data."""
    
    def get_quote(self, instruments: List[str]):
        """
        Get full market quote for instruments.
        
        Args:
            instruments (List[str]): List of instrument tokens (e.g., ['NSE:INFY', 'NSE:TCS'])
        """
        try:
            self.log_request("GET", "/quote", {'instruments': instruments})
            quote = self.kite.quote(instruments)
            self.log_response(quote, "SUCCESS")
            return quote
        except Exception as e:
            self.log_error(e, "get_quote")
            raise
    
    def get_ohlc(self, instruments: List[str]):
        """
        Get OHLC for instruments.
        
        Args:
            instruments (List[str]): List of instrument tokens
        """
        try:
            self.log_request("GET", "/quote/ohlc", {'instruments': instruments})
            ohlc = self.kite.ohlc(instruments)
            self.log_response(ohlc, "SUCCESS")
            return ohlc
        except Exception as e:
            self.log_error(e, "get_ohlc")
            raise
    
    def get_ltp(self, instruments: List[str]):
        """
        Get LTP (Last Traded Price) for instruments.
        
        Args:
            instruments (List[str]): List of instrument tokens
        """
        try:
            self.log_request("GET", "/quote/ltp", {'instruments': instruments})
            ltp = self.kite.ltp(instruments)
            self.log_response(ltp, "SUCCESS")
            return ltp
        except Exception as e:
            self.log_error(e, "get_ltp")
            raise
    
    def run_all_tests(self):
        """Run all market API tests."""
        results = {}
        
        # Test with NIFTY and common stocks
        instruments = ['NSE:NIFTY 50', 'NSE:INFY', 'NSE:TCS', 'NSE:RELIANCE']
        
        # Get quote
        try:
            results['quote'] = self.get_quote(instruments)
        except Exception as e:
            results['quote'] = f"Error: {str(e)}"
        
        # Get OHLC
        try:
            results['ohlc'] = self.get_ohlc(instruments)
        except Exception as e:
            results['ohlc'] = f"Error: {str(e)}"
        
        # Get LTP
        try:
            results['ltp'] = self.get_ltp(instruments)
        except Exception as e:
            results['ltp'] = f"Error: {str(e)}"
        
        return results

