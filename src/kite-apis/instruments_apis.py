"""
Instruments API client for Kite Connect.
"""
try:
    from .base_client import KiteAPIClient
except ImportError:
    from base_client import KiteAPIClient
from typing import List


class InstrumentsAPIs(KiteAPIClient):
    """APIs for instrument data."""
    
    def get_instruments(self, exchange: str = None):
        """
        Get list of all instruments.
        
        Args:
            exchange (str): Optional exchange name (NSE, BSE, MCX, etc.)
        """
        try:
            endpoint = f"/instruments{f'/{exchange}' if exchange else ''}"
            self.log_request("GET", endpoint)
            
            instruments = self.kite.instruments(exchange=exchange) if exchange else self.kite.instruments()
            self.log_response(f"Retrieved {len(instruments)} instruments", "SUCCESS")
            return instruments
        except Exception as e:
            self.log_error(e, "get_instruments")
            raise
    
    def get_quote(self, instruments: List[str]):
        """Get quote for instruments (delegates to MarketAPIs)."""
        try:
            self.log_request("GET", "/quote", {'instruments': instruments})
            quote = self.kite.quote(instruments)
            self.log_response(quote, "SUCCESS")
            return quote
        except Exception as e:
            self.log_error(e, "get_quote")
            raise
    
    def run_all_tests(self):
        """Run all instrument API tests."""
        results = {}
        
        # Get all instruments
        try:
            all_instruments = self.get_instruments()
            results['all_instruments_count'] = len(all_instruments)
            results['sample_instruments'] = all_instruments[:5] if len(all_instruments) > 5 else all_instruments
        except Exception as e:
            results['all_instruments'] = f"Error: {str(e)}"
        
        # Get NSE instruments
        try:
            nse_instruments = self.get_instruments('NSE')
            results['nse_instruments_count'] = len(nse_instruments)
        except Exception as e:
            results['nse_instruments'] = f"Error: {str(e)}"
        
        # Get BSE instruments
        try:
            bse_instruments = self.get_instruments('BSE')
            results['bse_instruments_count'] = len(bse_instruments)
        except Exception as e:
            results['bse_instruments'] = f"Error: {str(e)}"
        
        return results

