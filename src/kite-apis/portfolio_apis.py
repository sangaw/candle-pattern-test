"""
Portfolio API client for Kite Connect.
"""
try:
    from .base_client import KiteAPIClient
except ImportError:
    from base_client import KiteAPIClient


class PortfolioAPIs(KiteAPIClient):
    """APIs for portfolio management."""
    
    def get_holdings(self):
        """Get all holdings."""
        try:
            self.log_request("GET", "/portfolio/holdings")
            holdings = self.kite.holdings()
            self.log_response(holdings, "SUCCESS")
            return holdings
        except Exception as e:
            self.log_error(e, "get_holdings")
            raise
    
    def get_positions(self):
        """Get all positions."""
        try:
            self.log_request("GET", "/portfolio/positions")
            positions = self.kite.positions()
            self.log_response(positions, "SUCCESS")
            return positions
        except Exception as e:
            self.log_error(e, "get_positions")
            raise
    
    def convert_position(self, exchange: str, tradingsymbol: str,
                        transaction_type: str, position_type: str,
                        quantity: int, old_product: str, new_product: str):
        """Convert position (product change)."""
        try:
            params = {
                'exchange': exchange,
                'tradingsymbol': tradingsymbol,
                'transaction_type': transaction_type,
                'position_type': position_type,
                'quantity': quantity,
                'old_product': old_product,
                'new_product': new_product
            }
            
            self.log_request("PUT", "/portfolio/positions", params)
            
            # NOTE: This is commented to prevent accidental actions
            # converted = self.kite.convert_position(**params)
            # self.log_response(converted, "SUCCESS")
            # return converted
            
            self.log_response("POSITION CONVERSION SKIPPED (SAFETY)", "INFO")
            return "POSITION CONVERSION DISABLED"
            
        except Exception as e:
            self.log_error(e, "convert_position")
            raise
    
    def run_all_tests(self):
        """Run all portfolio API tests."""
        results = {}
        
        # Test holdings
        try:
            results['holdings'] = self.get_holdings()
        except Exception as e:
            results['holdings'] = f"Error: {str(e)}"
        
        # Test positions
        try:
            results['positions'] = self.get_positions()
        except Exception as e:
            results['positions'] = f"Error: {str(e)}"
        
        return results

