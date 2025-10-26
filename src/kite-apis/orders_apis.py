"""
Orders API client for Kite Connect.
"""
try:
    from .base_client import KiteAPIClient
except ImportError:
    from base_client import KiteAPIClient
from typing import Dict, Any


class OrdersAPIs(KiteAPIClient):
    """APIs for order management."""
    
    def place_order(self, variety: str, exchange: str, tradingsymbol: str,
                   transaction_type: str, quantity: int, price: float = None,
                   product: str = "MIS", order_type: str = "MARKET",
                   validity: str = "DAY", disclosed_quantity: int = 0,
                   trigger_price: float = 0, squareoff: float = 0, 
                   stoploss: float = 0, trailing_stoploss: float = 0,
                   tag: str = "API"):
        """
        Place an order (WARNING: This will execute real orders!)
        
        NOTE: This is commented out by default to prevent accidental trades.
        """
        try:
            params = {
                'variety': variety,
                'exchange': exchange,
                'tradingsymbol': tradingsymbol,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'product': product,
                'order_type': order_type,
                'validity': validity
            }
            
            if price:
                params['price'] = price
            if disclosed_quantity:
                params['disclosed_quantity'] = disclosed_quantity
            if trigger_price:
                params['trigger_price'] = trigger_price
            if squareoff:
                params['squareoff'] = squareoff
            if stoploss:
                params['stoploss'] = stoploss
            if trailing_stoploss:
                params['trailing_stoploss'] = trailing_stoploss
            if tag:
                params['tag'] = tag
            
            self.log_request("POST", "/orders/regular", params)
            
            # NOTE: This is commented to prevent accidental trades
            # order_id = self.kite.place_order(**params)
            # self.log_response(order_id, "SUCCESS")
            # return order_id
            
            self.log_response("ORDER PLACEMENT SKIPPED (SAFETY)", "INFO")
            return "ORDER PLACEMENT DISABLED - Uncomment in code to enable"
            
        except Exception as e:
            self.log_error(e, "place_order")
            raise
    
    def modify_order(self, order_id: str, variety: str, **kwargs):
        """Modify an existing order."""
        try:
            params = {'order_id': order_id, 'variety': variety}
            params.update(kwargs)
            
            self.log_request("PUT", f"/orders/{order_id}", params)
            
            # NOTE: This is commented to prevent accidental trades
            # modified_order = self.kite.modify_order(order_id, variety, **kwargs)
            # self.log_response(modified_order, "SUCCESS")
            # return modified_order
            
            self.log_response("ORDER MODIFICATION SKIPPED (SAFETY)", "INFO")
            return "ORDER MODIFICATION DISABLED - Uncomment in code to enable"
            
        except Exception as e:
            self.log_error(e, "modify_order")
            raise
    
    def cancel_order(self, order_id: str, variety: str = "regular"):
        """Cancel an order."""
        try:
            self.log_request("DELETE", f"/orders/{order_id}", {'variety': variety})
            
            # NOTE: This is commented to prevent accidental trades
            # cancelled = self.kite.cancel_order(order_id, variety)
            # self.log_response(cancelled, "SUCCESS")
            # return cancelled
            
            self.log_response("ORDER CANCELLATION SKIPPED (SAFETY)", "INFO")
            return "ORDER CANCELLATION DISABLED - Uncomment in code to enable"
            
        except Exception as e:
            self.log_error(e, "cancel_order")
            raise
    
    def get_order_history(self, order_id: str):
        """Get order history."""
        try:
            self.log_request("GET", f"/orders/history/{order_id}")
            history = self.kite.order_history(order_id)
            self.log_response(history, "SUCCESS")
            return history
        except Exception as e:
            self.log_error(e, "get_order_history")
            raise
    
    def run_all_tests(self):
        """Run all order API tests."""
        results = {}
        
        # Get orders
        try:
            results['get_orders'] = self.kite.orders()
        except Exception as e:
            results['get_orders'] = f"Error: {str(e)}"
        
        return results

