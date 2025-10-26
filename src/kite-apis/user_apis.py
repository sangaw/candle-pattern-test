"""
User API client for Kite Connect.
"""
try:
    from .base_client import KiteAPIClient
except ImportError:
    from base_client import KiteAPIClient


class UserAPIs(KiteAPIClient):
    """APIs for user data and preferences."""
    
    def get_profile(self):
        """Get user profile."""
        try:
            self.log_request("GET", "/user/profile")
            profile = self.kite.profile()
            self.log_response(profile, "SUCCESS")
            return profile
        except Exception as e:
            self.log_error(e, "get_profile")
            raise
    
    def get_margins(self, segment: str = None):
        """
        Get user margins.
        
        Args:
            segment (str): Optional segment ('equity' or 'commodity')
        """
        try:
            endpoint = f"/user/margins{f'/{segment}' if segment else ''}"
            self.log_request("GET", endpoint)
            
            if segment:
                margins = self.kite.margins(segment=segment)
            else:
                margins = self.kite.margins()
            
            self.log_response(margins, "SUCCESS")
            return margins
        except Exception as e:
            self.log_error(e, "get_margins")
            raise
    
    def get_orders(self):
        """Get all orders."""
        try:
            self.log_request("GET", "/orders")
            orders = self.kite.orders()
            self.log_response(orders, "SUCCESS")
            return orders
        except Exception as e:
            self.log_error(e, "get_orders")
            raise
    
    def get_positions(self):
        """Get positions."""
        try:
            self.log_request("GET", "/portfolio/positions")
            positions = self.kite.positions()
            self.log_response(positions, "SUCCESS")
            return positions
        except Exception as e:
            self.log_error(e, "get_positions")
            raise
    
    def get_holdings(self):
        """Get holdings."""
        try:
            self.log_request("GET", "/portfolio/holdings")
            holdings = self.kite.holdings()
            self.log_response(holdings, "SUCCESS")
            return holdings
        except Exception as e:
            self.log_error(e, "get_holdings")
            raise
    
    def run_all_tests(self):
        """Run all user API tests."""
        results = {}
        
        # Test profile
        try:
            results['profile'] = self.get_profile()
        except Exception as e:
            results['profile'] = f"Error: {str(e)}"
        
        # Test margins
        try:
            results['margins'] = self.get_margins()
        except Exception as e:
            results['margins'] = f"Error: {str(e)}"
        
        # Test equity margins
        try:
            results['margins_equity'] = self.get_margins('equity')
        except Exception as e:
            results['margins_equity'] = f"Error: {str(e)}"
        
        # Test commodity margins
        try:
            results['margins_commodity'] = self.get_margins('commodity')
        except Exception as e:
            results['margins_commodity'] = f"Error: {str(e)}"
        
        return results

