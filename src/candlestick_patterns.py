"""
Candlestick pattern recognition module.

This module provides functionality to identify various candlestick patterns
in OHLC data including single and multi-candle patterns.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from src.utils import (
    is_bullish, is_bearish, is_doji, is_hammer, is_shooting_star,
    calculate_body_size, calculate_shadow_size, validate_ohlc_data
)

logger = logging.getLogger(__name__)


class CandlestickPatternAnalyzer:
    """
    A class to analyze and identify candlestick patterns in OHLC data.
    
    Supports various patterns including:
    - Single candle patterns (Doji, Hammer, Shooting Star)
    - Multi-candle patterns (Engulfing, Morning Star, Evening Star)
    """
    
    def __init__(self):
        """Initialize the pattern analyzer."""
        self.patterns = {}
        
    def analyze_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze all candlestick patterns in the given data.
        
        Args:
            data (pd.DataFrame): OHLC data with columns ['Date', 'Open', 'High', 'Low', 'Close']
            
        Returns:
            pd.DataFrame: Original data with a single 'pattern' column added
        """
        if data.empty:
            logger.warning("Empty data provided for pattern analysis")
            return data
            
        if not validate_ohlc_data(data):
            logger.error("Invalid OHLC data provided")
            return data
            
        result = data.copy()
        result['pattern'] = ''
        
        # Analyze patterns for each row
        for idx in result.index:
            patterns = []
            row = result.loc[idx]
            open_price = row['Open']
            high = row['High']
            low = row['Low']
            close_price = row['Close']
            
            # Single candle patterns
            if is_doji(open_price, close_price):
                patterns.append('doji')
            if is_hammer(open_price, close_price, high, low):
                patterns.append('hammer')
            if is_shooting_star(open_price, close_price, high, low):
                patterns.append('shooting_star')
            
            # Multi-candle patterns (need previous/next rows)
            # Engulfing patterns (2 candles)
            if idx > 0:
                prev_row = result.loc[idx - 1]
                if self._is_bullish_engulfing(prev_row, row):
                    patterns.append('bullish_engulfing')
                if self._is_bearish_engulfing(prev_row, row):
                    patterns.append('bearish_engulfing')
            
            # Star patterns (3 candles)
            if idx > 1:
                prev_row_1 = result.loc[idx - 1]
                prev_row_2 = result.loc[idx - 2]
                if self._is_morning_star(prev_row_2, prev_row_1, row):
                    patterns.append('morning_star')
                if self._is_evening_star(prev_row_2, prev_row_1, row):
                    patterns.append('evening_star')
            
            result.at[idx, 'pattern'] = ','.join(patterns)
        
        logger.info(f"Pattern analysis completed for {len(data)} candles")
        return result
    
    def _is_bullish_engulfing(self, prev_candle: pd.Series, curr_candle: pd.Series) -> bool:
        """
        Check if current candle forms a bullish engulfing pattern with previous candle.
        
        Args:
            prev_candle (pd.Series): Previous candle data
            curr_candle (pd.Series): Current candle data
            
        Returns:
            bool: True if bullish engulfing pattern
        """
        # Previous candle should be bearish
        if not is_bearish(prev_candle['Open'], prev_candle['Close']):
            return False
            
        # Current candle should be bullish
        if not is_bullish(curr_candle['Open'], curr_candle['Close']):
            return False
            
        # Current candle should completely engulf previous candle
        curr_open = curr_candle['Open']
        curr_close = curr_candle['Close']
        prev_open = prev_candle['Open']
        prev_close = prev_candle['Close']
        
        return (curr_open < prev_close and curr_close > prev_open)
    
    def _is_bearish_engulfing(self, prev_candle: pd.Series, curr_candle: pd.Series) -> bool:
        """
        Check if current candle forms a bearish engulfing pattern with previous candle.
        
        Args:
            prev_candle (pd.Series): Previous candle data
            curr_candle (pd.Series): Current candle data
            
        Returns:
            bool: True if bearish engulfing pattern
        """
        # Previous candle should be bullish
        if not is_bullish(prev_candle['Open'], prev_candle['Close']):
            return False
            
        # Current candle should be bearish
        if not is_bearish(curr_candle['Open'], curr_candle['Close']):
            return False
            
        # Current candle should completely engulf previous candle
        curr_open = curr_candle['Open']
        curr_close = curr_candle['Close']
        prev_open = prev_candle['Open']
        prev_close = prev_candle['Close']
        
        return (curr_open > prev_close and curr_close < prev_open)
    
    def _is_morning_star(self, first_candle: pd.Series, second_candle: pd.Series, 
                        third_candle: pd.Series) -> bool:
        """
        Check if three candles form a morning star pattern.
        
        Args:
            first_candle (pd.Series): First candle (bearish)
            second_candle (pd.Series): Second candle (small body, doji-like)
            third_candle (pd.Series): Third candle (bullish)
            
        Returns:
            bool: True if morning star pattern
        """
        # First candle should be bearish
        if not is_bearish(first_candle['Open'], first_candle['Close']):
            return False
            
        # Second candle should be small (doji-like)
        if not is_doji(second_candle['Open'], second_candle['Close']):
            return False
            
        # Third candle should be bullish
        if not is_bullish(third_candle['Open'], third_candle['Close']):
            return False
            
        # Second candle should gap down from first
        first_close = first_candle['Close']
        second_open = second_candle['Open']
        second_close = second_candle['Close']
        third_open = third_candle['Open']
        
        # Check for gap down and gap up
        gap_down = second_open < first_close
        gap_up = third_open > second_close
        
        return gap_down and gap_up
    
    def _is_evening_star(self, first_candle: pd.Series, second_candle: pd.Series, 
                        third_candle: pd.Series) -> bool:
        """
        Check if three candles form an evening star pattern.
        
        Args:
            first_candle (pd.Series): First candle (bullish)
            second_candle (pd.Series): Second candle (small body, doji-like)
            third_candle (pd.Series): Third candle (bearish)
            
        Returns:
            bool: True if evening star pattern
        """
        # First candle should be bullish
        if not is_bullish(first_candle['Open'], first_candle['Close']):
            return False
            
        # Second candle should be small (doji-like)
        if not is_doji(second_candle['Open'], second_candle['Close']):
            return False
            
        # Third candle should be bearish
        if not is_bearish(third_candle['Open'], third_candle['Close']):
            return False
            
        # Second candle should gap up from first
        first_close = first_candle['Close']
        second_open = second_candle['Open']
        second_close = second_candle['Close']
        third_open = third_candle['Open']
        
        # Check for gap up and gap down
        gap_up = second_open > first_close
        gap_down = third_open < second_close
        
        return gap_up and gap_down
    
    def get_pattern_summary(self, data: pd.DataFrame) -> Dict[str, int]:
        """
        Get a summary of all patterns found in the data.
        
        Args:
            data (pd.DataFrame): Data with 'pattern' column
            
        Returns:
            Dict[str, int]: Pattern name and count
        """
        summary = {}
        if 'pattern' not in data.columns:
            return summary
        for pattern_name in ['doji', 'hammer', 'shooting_star', 'bullish_engulfing', 'bearish_engulfing', 'morning_star', 'evening_star']:
            summary[pattern_name] = data['pattern'].str.contains(pattern_name).sum()
        return summary
    
    def get_pattern_dates(self, data: pd.DataFrame, pattern_name: str) -> List[str]:
        """
        Get dates when a specific pattern occurred.
        
        Args:
            data (pd.DataFrame): Data with 'pattern' column
            pattern_name (str): Name of the pattern to search for
            
        Returns:
            List[str]: List of dates when pattern occurred
        """
        if 'pattern' not in data.columns:
            logger.warning(f"Pattern column not found in data")
            return []
        if 'Date' not in data.columns:
            logger.warning(f"Date column not found in data")
            return []
        pattern_dates = data[data['pattern'].str.contains(pattern_name, na=False)]['Date'].tolist()
        return pattern_dates

    def process_csv_file(self, input_file_path: str, output_file_path: str = None) -> str:
        """
        Process a CSV file containing OHLC data and add candlestick pattern columns.
        
        Args:
            input_file_path (str): Path to the input CSV file
            output_file_path (str): Path for the output CSV file. If None, will be auto-generated.
            
        Returns:
            str: Path to the output CSV file
        """
        logger.info(f"Processing CSV file: {input_file_path}")
        
        try:
            # Read the CSV file
            logger.debug(f"Reading data from {input_file_path}")
            data = pd.read_csv(input_file_path)
            
            # Check if required columns exist
            required_columns = ['date', 'open', 'high', 'low', 'close']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                logger.error(f"Available columns: {list(data.columns)}")
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            logger.info(f"Successfully read {len(data)} rows from {input_file_path}")
            
            # Convert date column to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(data['date']):
                data['date'] = pd.to_datetime(data['date'])
                logger.debug("Converted date column to datetime")
            
            # Rename columns to match the analyzer's expected format (capitalized)
            column_mapping = {
                'date': 'Date',
                'open': 'Open', 
                'high': 'High',
                'low': 'Low',
                'close': 'Close'
            }
            
            # Only rename columns that exist
            existing_columns = {k: v for k, v in column_mapping.items() if k in data.columns}
            data = data.rename(columns=existing_columns)
            
            logger.debug(f"Renamed columns: {existing_columns}")
            
            # Sort by date to ensure chronological order
            data = data.sort_values('Date').reset_index(drop=True)
            logger.debug("Sorted data by date")
            
            # Analyze patterns
            logger.info("Starting candlestick pattern analysis")
            result = self.analyze_patterns(data)
            
            # Generate output filename if not provided
            if output_file_path is None:
                input_name = input_file_path.replace('.csv', '')
                output_file_path = f"{input_name}_with_patterns.csv"
            
            # Save the result
            logger.info(f"Saving result to {output_file_path}")
            result.to_csv(output_file_path, index=False)
            
            # Log summary
            pattern_summary = self.get_pattern_summary(result)
            logger.info(f"Pattern analysis completed. Found patterns: {pattern_summary}")
            
            # Print summary to console
            print(f"\nCandlestick Pattern Analysis Summary:")
            print(f"Input file: {input_file_path}")
            print(f"Output file: {output_file_path}")
            print(f"Total candles analyzed: {len(result)}")
            print(f"Patterns found:")
            for pattern, count in pattern_summary.items():
                if count > 0:
                    print(f"  - {pattern}: {count}")
            
            return output_file_path
            
        except Exception as e:
            logger.error(f"Error processing CSV file {input_file_path}: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            raise

    def process_latest_nifty_file(self, data_directory: str = 'data') -> str:
        """
        Process the latest NIFTY CSV file in the data directory.
        
        Args:
            data_directory (str): Directory containing CSV files
            
        Returns:
            str: Path to the output CSV file
        """
        import os
        import glob
        
        logger.info(f"Looking for NIFTY CSV files in {data_directory}")
        
        # Find all NIFTY CSV files
        pattern = os.path.join(data_directory, "NIFTY_*.csv")
        nifty_files = glob.glob(pattern)
        
        if not nifty_files:
            logger.error(f"No NIFTY CSV files found in {data_directory}")
            raise FileNotFoundError(f"No NIFTY CSV files found in {data_directory}")
        
        # Sort by modification time to get the latest
        latest_file = max(nifty_files, key=os.path.getmtime)
        logger.info(f"Found latest NIFTY file: {latest_file}")
        
        return self.process_csv_file(latest_file) 