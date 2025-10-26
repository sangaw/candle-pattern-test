"""
GTT (Good Till Triggered) API client for Kite Connect.
"""
try:
    from .base_client import KiteAPIClient
except ImportError:
    from base_client import KiteAPIClient
from typing import Dict, Any


class GTTAPIs(KiteAPIClient):
    """APIs for GTT order management."""
    
    def get_gtt_list(self):
        """Get list of all GTT orders."""
        try:
            self.log_request("GET", "/gtt/triggers")
            gtt_list = self.kite.gtts()
            self.log_response(gtt_list, "SUCCESS")
            return gtt_list
        except Exception as e:
            self.log_error(e, "get_gtt_list")
            raise
    
    def get_gtt(self, trigger_id: int):
        """Get specific GTT order."""
        try:
            self.log_request("GET", f"/gtt/triggers/{trigger_id}")
            gtt = self.kite.gtt(trigger_id)
            self.log_response(gtt, "SUCCESS")
            return gtt
        except Exception as e:
            self.log_error(e, "get_gtt")
            raise
    
    def place_gtt(self, condition: Dict[str, Any], orders: list):
        """
        Place a GTT order (commented for safety).
        
        Args:
            condition: GTT condition dict
            orders: List of orders to place when triggered
        """
        try:
            params = {'condition': condition, 'orders': orders}
            self.log_request("POST", "/gtt/triggers", params)
            
            # NOTE: Disabled for safety
            # gtt_id = self.kite.place_gtt(**params)
            # self.log_response(gtt_id, "SUCCESS")
            # return gtt_id
            
            self.log_response("GTT PLACEMENT SKIPPED (SAFETY)", "INFO")
            return "GTT PLACEMENT DISABLED"
            
        except Exception as e:
            self.log_error(e, "place_gtt")
            raise
    
    def modify_gtt(self, trigger_id: int, condition: Dict[str, Any], orders: list):
        """Modify GTT order (commented for safety)."""
        try:
            params = {'condition': condition, 'orders': orders}
            self.log_request("PUT", f"/gtt/triggers/{trigger_id}", params)
            
            # NOTE: Disabled for safety
            # modified = self.kite.modify_gtt(trigger_id, condition, orders)
            # self.log_response(modified, "SUCCESS")
            # return modified
            
            self.log_response("GTT MODIFICATION SKIPPED (SAFETY)", "INFO")
            return "GTT MODIFICATION DISABLED"
            
        except Exception as e:
            self.log_error(e, "modify_gtt")
            raise
    
    def delete_gtt(self, trigger_id: int):
        """Delete GTT order (commented for safety)."""
        try:
            self.log_request("DELETE", f"/gtt/triggers/{trigger_id}")
            
            # NOTE: Disabled for safety
            # deleted = self.kite.delete_gtt(trigger_id)
            # self.log_response(deleted, "SUCCESS")
            # return deleted
            
            self.log_response("GTT DELETION SKIPPED (SAFETY)", "INFO")
            return "GTT DELETION DISABLED"
            
        except Exception as e:
            self.log_error(e, "delete_gtt")
            raise
    
    def run_all_tests(self):
        """Run all GTT API tests."""
        results = {}
        
        # Get GTT list
        try:
            results['gtt_list'] = self.get_gtt_list()
        except Exception as e:
            results['gtt_list'] = f"Error: {str(e)}"
        
        return results

