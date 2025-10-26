"""
Mutual funds API client for Kite Connect.
"""
try:
    from .base_client import KiteAPIClient
except ImportError:
    from base_client import KiteAPIClient


class MutualFundsAPIs(KiteAPIClient):
    """APIs for mutual fund operations."""
    
    def get_mf_instruments(self):
        """Get list of all MF instruments."""
        try:
            self.log_request("GET", "/mf/instruments")
            instruments = self.kite.mf_instruments()
            self.log_response(f"Retrieved {len(instruments)} MF instruments", "SUCCESS")
            return instruments
        except Exception as e:
            self.log_error(e, "get_mf_instruments")
            raise
    
    def place_mf_order(self, tradingsymbol: str, transaction_type: str, 
                      amount: float, tag: str = None):
        """Place MF order (commented for safety)."""
        try:
            params = {
                'tradingsymbol': tradingsymbol,
                'transaction_type': transaction_type,
                'amount': amount
            }
            if tag:
                params['tag'] = tag
            
            self.log_request("POST", "/mf/orders", params)
            
            # NOTE: Disabled for safety
            # order_id = self.kite.place_mf_order(**params)
            # self.log_response(order_id, "SUCCESS")
            # return order_id
            
            self.log_response("MF ORDER PLACEMENT SKIPPED (SAFETY)", "INFO")
            return "MF ORDER PLACEMENT DISABLED"
            
        except Exception as e:
            self.log_error(e, "place_mf_order")
            raise
    
    def cancel_mf_order(self, order_id: str):
        """Cancel MF order (commented for safety)."""
        try:
            self.log_request("DELETE", f"/mf/orders/{order_id}")
            
            # NOTE: Disabled for safety
            # cancelled = self.kite.cancel_mf_order(order_id)
            # self.log_response(cancelled, "SUCCESS")
            # return cancelled
            
            self.log_response("MF ORDER CANCELLATION SKIPPED (SAFETY)", "INFO")
            return "MF ORDER CANCELLATION DISABLED"
            
        except Exception as e:
            self.log_error(e, "cancel_mf_order")
            raise
    
    def get_mf_sips(self):
        """Get MF SIPs."""
        try:
            self.log_request("GET", "/mf/sips")
            sips = self.kite.mf_sips()
            self.log_response(sips, "SUCCESS")
            return sips
        except Exception as e:
            self.log_error(e, "get_mf_sips")
            raise
    
    def run_all_tests(self):
        """Run all mutual funds API tests."""
        results = {}
        
        # Get MF instruments
        try:
            results['mf_instruments'] = self.get_mf_instruments()
            results['mf_instruments_count'] = len(results['mf_instruments'])
            results['sample_mf_instruments'] = results['mf_instruments'][:5] if len(results['mf_instruments']) > 5 else results['mf_instruments']
        except Exception as e:
            results['mf_instruments'] = f"Error: {str(e)}"
        
        # Get MF SIPs
        try:
            results['mf_sips'] = self.get_mf_sips()
        except Exception as e:
            results['mf_sips'] = f"Error: {str(e)}"
        
        return results

