"""
Historical data API client for Kite Connect.
"""
try:
    from .base_client import KiteAPIClient
except ImportError:
    from base_client import KiteAPIClient
from datetime import datetime, timedelta


class HistoricalAPIs(KiteAPIClient):
    """APIs for historical data."""
    
    def get_historical_data(self, instrument_token: int, from_date: str, to_date: str,
                           interval: str = 'day', continuous: bool = False,
                           oi: bool = False):
        """
        Get historical candle data.
        
        Args:
            instrument_token (int): Instrument token
            from_date (str): Start date (YYYY-MM-DD)
            to_date (str): End date (YYYY-MM-DD)
            interval (str): Candle interval (minute, 3minute, 5minute, 15minute, 30minute, hour, day)
            continuous (bool): Include expired contracts
            oi (bool): Include open interest data
        """
        try:
            params = {
                'instrument_token': instrument_token,
                'from_date': datetime.strptime(from_date, '%Y-%m-%d'),
                'to_date': datetime.strptime(to_date, '%Y-%m-%d'),
                'interval': interval,
                'continuous': continuous,
                'oi': oi
            }
            
            self.log_request("GET", f"/instruments/historical/{instrument_token}", params)
            data = self.kite.historical_data(**params)
            self.log_response(f"Retrieved {len(data)} candles", "SUCCESS")
            return data
        except Exception as e:
            self.log_error(e, "get_historical_data")
            raise
    
    def run_all_tests(self):
        """Run all historical API tests."""
        results = {}
        
        # Get NIFTY historical data for last 30 days
        try:
            to_date = datetime.now()
            from_date = to_date - timedelta(days=30)
            
            results['nifty_historical'] = self.get_historical_data(
                instrument_token=256265,  # NIFTY 50
                from_date=from_date.strftime('%Y-%m-%d'),
                to_date=to_date.strftime('%Y-%m-%d'),
                interval='day'
            )
            results['nifty_historical_count'] = len(results['nifty_historical'])
        except Exception as e:
            results['nifty_historical'] = f"Error: {str(e)}"
        
        # Test different intervals
        intervals = ['day', 'hour', '30minute']
        for interval in intervals:
            try:
                to_date = datetime.now()
                from_date = to_date - timedelta(days=5)
                
                data = self.get_historical_data(
                    instrument_token=256265,
                    from_date=from_date.strftime('%Y-%m-%d'),
                    to_date=to_date.strftime('%Y-%m-%d'),
                    interval=interval
                )
                results[f'historical_{interval}'] = len(data)
            except Exception as e:
                results[f'historical_{interval}'] = f"Error: {str(e)}"
        
        return results

