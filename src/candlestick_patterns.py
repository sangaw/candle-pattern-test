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
            pd.DataFrame: Original data with pattern columns added
        """
        if data.empty:
            logger.warning("Empty data provided for pattern analysis")
            return data
            
        if not validate_ohlc_data(data):
            logger.error("Invalid OHLC data provided")
            return data
            
        # Create a copy to avoid modifying original data
        result = data.copy()
        
        # Analyze single candle patterns
        result = self._analyze_single_candle_patterns(result)
        
        # Analyze multi-candle patterns
        result = self._analyze_multi_candle_patterns(result)
        
        logger.info(f"Pattern analysis completed for {len(data)} candles")
        return result
    
    def _analyze_single_candle_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze single candle patterns.
        
        Args:
            data (pd.DataFrame): OHLC data
            
        Returns:
            pd.DataFrame: Data with single candle pattern columns
        """
        # Initialize pattern columns
        data['is_doji'] = False
        data['is_hammer'] = False
        data['is_shooting_star'] = False
        data['is_bullish'] = False
        data['is_bearish'] = False
        
        for idx, row in data.iterrows():
            open_price = row['Open']
            high = row['High']
            low = row['Low']
            close_price = row['Close']
            
            # Check basic bullish/bearish
            data.at[idx, 'is_bullish'] = is_bullish(open_price, close_price)
            data.at[idx, 'is_bearish'] = is_bearish(open_price, close_price)
            
            # Check Doji
            data.at[idx, 'is_doji'] = is_doji(open_price, close_price)
            
            # Check Hammer
            data.at[idx, 'is_hammer'] = is_hammer(open_price, close_price, high, low)
            
            # Check Shooting Star
            data.at[idx, 'is_shooting_star'] = is_shooting_star(open_price, close_price, high, low)
        
        return data
    
    def _analyze_multi_candle_patterns(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze multi-candle patterns.
        
        Args:
            data (pd.DataFrame): OHLC data
            
        Returns:
            pd.DataFrame: Data with multi-candle pattern columns
        """
        # Initialize pattern columns
        data['is_bullish_engulfing'] = False
        data['is_bearish_engulfing'] = False
        data['is_morning_star'] = False
        data['is_evening_star'] = False
        
        # Need at least 2 candles for engulfing patterns
        if len(data) < 2:
            return data
            
        # Need at least 3 candles for star patterns
        if len(data) < 3:
            return data
        
        for i in range(1, len(data)):
            # Engulfing patterns (2 candles)
            if self._is_bullish_engulfing(data.iloc[i-1], data.iloc[i]):
                data.at[data.index[i], 'is_bullish_engulfing'] = True
                
            if self._is_bearish_engulfing(data.iloc[i-1], data.iloc[i]):
                data.at[data.index[i], 'is_bearish_engulfing'] = True
        
        for i in range(2, len(data)):
            # Star patterns (3 candles)
            if self._is_morning_star(data.iloc[i-2], data.iloc[i-1], data.iloc[i]):
                data.at[data.index[i], 'is_morning_star'] = True
                
            if self._is_evening_star(data.iloc[i-2], data.iloc[i-1], data.iloc[i]):
                data.at[data.index[i], 'is_evening_star'] = True
        
        return data
    
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
            data (pd.DataFrame): Data with pattern columns
            
        Returns:
            Dict[str, int]: Pattern name and count
        """
        pattern_columns = [
            'is_doji', 'is_hammer', 'is_shooting_star',
            'is_bullish_engulfing', 'is_bearish_engulfing',
            'is_morning_star', 'is_evening_star'
        ]
        
        summary = {}
        for col in pattern_columns:
            if col in data.columns:
                summary[col] = data[col].sum()
        
        return summary
    
    def get_pattern_dates(self, data: pd.DataFrame, pattern_name: str) -> List[str]:
        """
        Get dates when a specific pattern occurred.
        
        Args:
            data (pd.DataFrame): Data with pattern columns
            pattern_name (str): Name of the pattern to search for
            
        Returns:
            List[str]: List of dates when pattern occurred
        """
        if pattern_name not in data.columns:
            logger.warning(f"Pattern {pattern_name} not found in data")
            return []
            
        pattern_dates = data[data[pattern_name]]['Date'].tolist()
        return pattern_dates 