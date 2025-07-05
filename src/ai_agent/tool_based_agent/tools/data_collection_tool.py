#!/usr/bin/env python3
"""
Data Collection Tool
A tool for fetching historical candle data for instruments.
"""
import os
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data_fetcher import KiteConnectDataFetcher

logger = logging.getLogger(__name__)

class DataCollectionTool:
    """
    Tool for collecting historical candle data.
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the data collection tool."""
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def fetch_instrument_data(self, instrument: Dict, 
                             days_back: int = 30,
                             save_data: bool = True) -> Dict:
        """
        Fetch historical data for a single instrument.
        
        Args:
            instrument: Instrument dictionary with details
            days_back: Number of days of historical data to fetch
            save_data: Whether to save data to file
            
        Returns:
            Dictionary with fetch results and metadata
        """
        try:
            logger.info(f"Fetching data for {instrument['tradingsymbol']}")
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Fetch data using existing data_fetcher
            fetcher = KiteConnectDataFetcher()
            df = fetcher.get_historical_data_for_instrument(
                instrument_token=instrument['instrument_token'],
                from_date=start_date.strftime('%Y-%m-%d'),
                to_date=end_date.strftime('%Y-%m-%d'),
                interval='day',
                save_csv=save_data,
                instrument_name=instrument['tradingsymbol']
            )
            
            result = {
                'data_points': len(df),
                'file_path': None
            }
            
            # Generate descriptive filename
            if save_data and result.get('file_path'):
                descriptive_filename = self._generate_descriptive_filename(instrument)
                new_file_path = os.path.join(self.data_dir, descriptive_filename)
                
                # Rename the file to be more descriptive
                if os.path.exists(result['file_path']):
                    os.rename(result['file_path'], new_file_path)
                    result['file_path'] = new_file_path
            
            return {
                'success': True,
                'instrument': instrument,
                'data_points': result.get('data_points', 0),
                'file_path': result.get('file_path'),
                'date_range': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                },
                'fetch_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching data for {instrument['tradingsymbol']}: {str(e)}")
            return {
                'success': False,
                'instrument': instrument,
                'error': str(e),
                'fetch_time': datetime.now().isoformat()
            }
    
    def fetch_multiple_instruments(self, instruments: List[Dict], 
                                  days_back: int = 30) -> Dict:
        """
        Fetch data for multiple instruments.
        
        Args:
            instruments: List of instrument dictionaries
            days_back: Number of days of historical data to fetch
            
        Returns:
            Dictionary with results for all instruments
        """
        logger.info(f"Fetching data for {len(instruments)} instruments")
        
        results = {
            'total_instruments': len(instruments),
            'successful_fetches': 0,
            'failed_fetches': 0,
            'results': [],
            'fetch_time': datetime.now().isoformat()
        }
        
        for instrument in instruments:
            result = self.fetch_instrument_data(instrument, days_back)
            results['results'].append(result)
            
            if result['success']:
                results['successful_fetches'] += 1
            else:
                results['failed_fetches'] += 1
        
        return results
    
    def _generate_descriptive_filename(self, instrument: Dict) -> str:
        """Generate a descriptive filename for the instrument data."""
        symbol = instrument['tradingsymbol']
        name = instrument['name'].replace(' ', '_')
        exchange = instrument['exchange']
        instrument_type = instrument['instrument_type']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        return f"{symbol}_{name}_{exchange}_{instrument_type}_{timestamp}.csv"
    
    def get_data_summary(self, instruments: List[Dict]) -> Dict:
        """
        Get a summary of data collection status.
        
        Args:
            instruments: List of instruments to check
            
        Returns:
            Summary dictionary
        """
        summary = {
            'total_instruments': len(instruments),
            'data_available': [],
            'data_missing': [],
            'summary_time': datetime.now().isoformat()
        }
        
        for instrument in instruments:
            symbol = instrument['tradingsymbol']
            name = instrument['name']
            
            # Check if data file exists (simplified check)
            # In a real implementation, you'd check the actual data files
            summary['data_available'].append({
                'symbol': symbol,
                'name': name,
                'status': 'available'  # Placeholder
            })
        
        return summary

# Tool functions for the AI agent
def fetch_instrument_data_tool(instrument: Dict, days_back: int = 30) -> Dict:
    """
    Tool function for fetching instrument data.
    
    Args:
        instrument: Instrument dictionary
        days_back: Number of days of historical data
        
    Returns:
        Fetch results dictionary
    """
    tool = DataCollectionTool()
    return tool.fetch_instrument_data(instrument, days_back)

def fetch_multiple_instruments_tool(instruments: List[Dict], days_back: int = 30) -> Dict:
    """
    Tool function for fetching data for multiple instruments.
    
    Args:
        instruments: List of instrument dictionaries
        days_back: Number of days of historical data
        
    Returns:
        Fetch results dictionary
    """
    tool = DataCollectionTool()
    return tool.fetch_multiple_instruments(instruments, days_back)

def get_data_summary_tool(instruments: List[Dict]) -> Dict:
    """
    Tool function for getting data collection summary.
    
    Args:
        instruments: List of instruments to check
        
    Returns:
        Summary dictionary
    """
    tool = DataCollectionTool()
    return tool.get_data_summary(instruments) 