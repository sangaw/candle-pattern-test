"""
Workflow module for automated data analysis processes.

This module contains workflow scripts that orchestrate multiple analysis steps
including data fetching, pattern analysis, and report generation.
"""

from .nifty_data_analysis import (
    NiftyDataAnalysisWorkflow,
    DataFetchRequest,
    PatternAnalysisRequest,
    AnalysisResult
)

__all__ = [
    'NiftyDataAnalysisWorkflow',
    'DataFetchRequest', 
    'PatternAnalysisRequest',
    'AnalysisResult'
] 