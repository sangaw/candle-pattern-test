"""
NIFTY Candlestick Pattern Tester

A Python package for analyzing candlestick patterns in NIFTY data.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from src.data_fetcher import KiteConnectDataFetcher
from src.candlestick_patterns import CandlestickPatternAnalyzer
from src.utils import calculate_body_size, calculate_shadow_size

__all__ = [
    "KiteConnectDataFetcher",
    "CandlestickPatternAnalyzer", 
    "calculate_body_size",
    "calculate_shadow_size"
] 