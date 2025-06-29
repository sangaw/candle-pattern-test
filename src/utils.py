"""
Utility functions for candlestick pattern analysis.

This module contains helper functions for calculating various
candlestick properties and pattern recognition.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


def calculate_body_size(open_price: float, close_price: float) -> float:
    """
    Calculate the body size of a candlestick.
    
    Args:
        open_price (float): Opening price
        close_price (float): Closing price
        
    Returns:
        float: Absolute body size
    """
    return abs(close_price - open_price)


def calculate_shadow_size(high: float, low: float, open_price: float, close_price: float) -> Tuple[float, float]:
    """
    Calculate upper and lower shadow sizes.
    
    Args:
        high (float): High price
        low (float): Low price
        open_price (float): Opening price
        close_price (float): Closing price
        
    Returns:
        Tuple[float, float]: (upper_shadow, lower_shadow)
    """
    body_high = max(open_price, close_price)
    body_low = min(open_price, close_price)
    
    upper_shadow = high - body_high
    lower_shadow = body_low - low
    
    return upper_shadow, lower_shadow


def is_bullish(open_price: float, close_price: float) -> bool:
    """
    Check if a candlestick is bullish (close > open).
    
    Args:
        open_price (float): Opening price
        close_price (float): Closing price
        
    Returns:
        bool: True if bullish, False otherwise
    """
    return close_price > open_price


def is_bearish(open_price: float, close_price: float) -> bool:
    """
    Check if a candlestick is bearish (close < open).
    
    Args:
        open_price (float): Opening price
        close_price (float): Closing price
        
    Returns:
        bool: True if bearish, False otherwise
    """
    return close_price < open_price


def calculate_body_percentage(open_price: float, close_price: float, high: float, low: float) -> float:
    """
    Calculate body size as a percentage of total range.
    
    Args:
        open_price (float): Opening price
        close_price (float): Closing price
        high (float): High price
        low (float): Low price
        
    Returns:
        float: Body size as percentage of total range
    """
    body_size = calculate_body_size(open_price, close_price)
    total_range = high - low
    
    if total_range == 0:
        return 0.0
    
    return (body_size / total_range) * 100


def calculate_shadow_percentages(high: float, low: float, open_price: float, close_price: float) -> Tuple[float, float]:
    """
    Calculate upper and lower shadows as percentages of total range.
    
    Args:
        high (float): High price
        low (float): Low price
        open_price (float): Opening price
        close_price (float): Closing price
        
    Returns:
        Tuple[float, float]: (upper_shadow_pct, lower_shadow_pct)
    """
    upper_shadow, lower_shadow = calculate_shadow_size(high, low, open_price, close_price)
    total_range = high - low
    
    if total_range == 0:
        return 0.0, 0.0
    
    upper_shadow_pct = (upper_shadow / total_range) * 100
    lower_shadow_pct = (lower_shadow / total_range) * 100
    
    return upper_shadow_pct, lower_shadow_pct


def get_candlestick_properties(row: pd.Series) -> Dict[str, Any]:
    """
    Get all candlestick properties for a given row.
    
    Args:
        row (pd.Series): DataFrame row with OHLC data
        
    Returns:
        Dict: Dictionary containing all candlestick properties
    """
    open_price = row['Open']
    high = row['High']
    low = row['Low']
    close_price = row['Close']
    
    body_size = calculate_body_size(open_price, close_price)
    upper_shadow, lower_shadow = calculate_shadow_size(high, low, open_price, close_price)
    body_pct = calculate_body_percentage(open_price, close_price, high, low)
    upper_shadow_pct, lower_shadow_pct = calculate_shadow_percentages(high, low, open_price, close_price)
    
    return {
        'body_size': body_size,
        'upper_shadow': upper_shadow,
        'lower_shadow': lower_shadow,
        'body_percentage': body_pct,
        'upper_shadow_percentage': upper_shadow_pct,
        'lower_shadow_percentage': lower_shadow_pct,
        'is_bullish': is_bullish(open_price, close_price),
        'is_bearish': is_bearish(open_price, close_price),
        'total_range': high - low
    }


def is_doji(open_price: float, close_price: float, tolerance: float = 0.1) -> bool:
    """
    Check if a candlestick is a doji (very small body).
    
    Args:
        open_price (float): Opening price
        close_price (float): Closing price
        tolerance (float): Maximum body size as percentage of total range
        
    Returns:
        bool: True if doji, False otherwise
    """
    body_size = calculate_body_size(open_price, close_price)
    total_range = max(open_price, close_price) - min(open_price, close_price)
    
    if total_range == 0:
        return True
    
    body_percentage = (body_size / total_range) * 100
    return body_percentage <= tolerance


def is_hammer(open_price: float, close_price: float, high: float, low: float, 
              body_threshold: float = 30.0, shadow_threshold: float = 60.0) -> bool:
    """
    Check if a candlestick is a hammer pattern.
    
    Args:
        open_price (float): Opening price
        close_price (float): Closing price
        high (float): High price
        low (float): Low price
        body_threshold (float): Maximum body size as percentage
        shadow_threshold (float): Minimum lower shadow as percentage
        
    Returns:
        bool: True if hammer, False otherwise
    """
    body_pct = calculate_body_percentage(open_price, close_price, high, low)
    _, lower_shadow_pct = calculate_shadow_percentages(high, low, open_price, close_price)
    
    return body_pct <= body_threshold and lower_shadow_pct >= shadow_threshold


def is_shooting_star(open_price: float, close_price: float, high: float, low: float,
                     body_threshold: float = 30.0, shadow_threshold: float = 60.0) -> bool:
    """
    Check if a candlestick is a shooting star pattern.
    
    Args:
        open_price (float): Opening price
        close_price (float): Closing price
        high (float): High price
        low (float): Low price
        body_threshold (float): Maximum body size as percentage
        shadow_threshold (float): Minimum upper shadow as percentage
        
    Returns:
        bool: True if shooting star, False otherwise
    """
    body_pct = calculate_body_percentage(open_price, close_price, high, low)
    upper_shadow_pct, _ = calculate_shadow_percentages(high, low, open_price, close_price)
    
    return body_pct <= body_threshold and upper_shadow_pct >= shadow_threshold


def validate_ohlc_data(data: pd.DataFrame) -> bool:
    """
    Validate that the OHLC data is consistent.
    
    Args:
        data (pd.DataFrame): DataFrame with OHLC columns
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_columns = ['Open', 'High', 'Low', 'Close']
    
    # Check if all required columns exist
    if not all(col in data.columns for col in required_columns):
        logger.error("Missing required OHLC columns")
        return False
    
    # Check for logical consistency
    for _, row in data.iterrows():
        if not (row['Low'] <= row['Open'] <= row['High'] and 
                row['Low'] <= row['Close'] <= row['High']):
            logger.error(f"Invalid OHLC data: {row}")
            return False
    
    return True 