#!/usr/bin/env python3
"""
NIFTY Data Analysis Workflow
A comprehensive workflow to fetch NIFTY data for 2025 and analyze candlestick patterns.

This script uses Pydantic AI to orchestrate the data fetching and pattern analysis process.
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_fetcher import KiteConnectDataFetcher
from candlestick_patterns import CandlestickPatternAnalyzer
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/nifty_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Pydantic models for data validation
class DataFetchRequest(BaseModel):
    """Model for data fetch requests."""
    instrument_name: str = Field(default="NIFTY", description="Name of the instrument")
    from_date: str = Field(description="Start date in YYYY-MM-DD format")
    to_date: str = Field(description="End date in YYYY-MM-DD format")
    interval: str = Field(default="day", description="Candle interval (day, minute, etc.)")
    save_csv: bool = Field(default=True, description="Whether to save data as CSV")

class PatternAnalysisRequest(BaseModel):
    """Model for pattern analysis requests."""
    csv_file_path: str = Field(description="Path to the CSV file to analyze")
    output_file_path: Optional[str] = Field(default=None, description="Output file path for results")

class AnalysisResult(BaseModel):
    """Model for analysis results."""
    total_candles: int
    patterns_found: Dict[str, int]
    pattern_dates: Dict[str, List[str]]
    analysis_summary: str
    output_file: str

class NiftyDataAnalysisWorkflow:
    """
    A comprehensive workflow for NIFTY data analysis using Pydantic AI.
    
    This class orchestrates the entire process:
    1. Fetch NIFTY data for 2025
    2. Save data as CSV
    3. Analyze candlestick patterns
    4. Generate comprehensive reports
    """
    
    def __init__(self):
        """Initialize the workflow components."""
        self.data_fetcher = KiteConnectDataFetcher()
        self.pattern_analyzer = CandlestickPatternAnalyzer()
        
        # Ensure data directory exists
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        logger.info("NiftyDataAnalysisWorkflow initialized successfully")
    
    def fetch_nifty_data_2025(self) -> str:
        """
        Fetch NIFTY data for the entire year 2025.
        
        Returns:
            str: Path to the saved CSV file
        """
        logger.info("Starting NIFTY data fetch for 2025")
        
        # Define date range for 2025
        from_date = "2025-01-01"
        to_date = "2025-12-31"
        
        try:
            # Fetch historical data
            df = self.data_fetcher.get_historical_data(
                from_date=from_date,
                to_date=to_date,
                interval='day'
            )
            
            if df.empty:
                logger.warning("No data fetched for the specified date range")
                return ""
            
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"nifty_daily_2025_{timestamp}.csv"
            csv_path = self.data_dir / csv_filename
            
            # Ensure column names are correct
            if 'date' in df.columns:
                df = df.rename(columns={
                    'date': 'Date',
                    'open': 'Open',
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                })
            
            df.to_csv(csv_path, index=False)
            logger.info(f"NIFTY data saved to: {csv_path}")
            logger.info(f"Fetched {len(df)} daily candles for 2025")
            
            return str(csv_path)
            
        except Exception as e:
            logger.error(f"Error fetching NIFTY data: {str(e)}")
            raise
    
    def analyze_candlestick_patterns(self, csv_file_path: str) -> AnalysisResult:
        """
        Analyze candlestick patterns in the provided CSV file.
        
        Args:
            csv_file_path (str): Path to the CSV file containing OHLC data
            
        Returns:
            AnalysisResult: Comprehensive analysis results
        """
        logger.info(f"Starting candlestick pattern analysis for: {csv_file_path}")
        
        try:
            # Load data
            df = pd.read_csv(csv_file_path)
            logger.info(f"Loaded {len(df)} rows from CSV")
            
            # Analyze patterns
            df_with_patterns = self.pattern_analyzer.analyze_patterns(df)
            
            # Get pattern summary
            pattern_summary = self.pattern_analyzer.get_pattern_summary(df_with_patterns)
            
            # Get pattern dates for each pattern type
            pattern_dates = {}
            for pattern_name in pattern_summary.keys():
                dates = self.pattern_analyzer.get_pattern_dates(df_with_patterns, pattern_name)
                pattern_dates[pattern_name] = dates
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"nifty_pattern_analysis_{timestamp}.csv"
            output_path = self.data_dir / output_filename
            
            df_with_patterns.to_csv(output_path, index=False)
            
            # Generate analysis summary
            analysis_summary = self._generate_analysis_summary(
                df_with_patterns, pattern_summary, pattern_dates
            )
            
            result = AnalysisResult(
                total_candles=len(df_with_patterns),
                patterns_found=pattern_summary,
                pattern_dates=pattern_dates,
                analysis_summary=analysis_summary,
                output_file=str(output_path)
            )
            
            logger.info(f"Pattern analysis completed. Results saved to: {output_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing candlestick patterns: {str(e)}")
            raise
    
    def _generate_analysis_summary(self, df: pd.DataFrame, pattern_summary: Dict[str, int], 
                                 pattern_dates: Dict[str, List[str]]) -> str:
        """
        Generate a comprehensive analysis summary.
        
        Args:
            df (pd.DataFrame): DataFrame with pattern analysis
            pattern_summary (Dict[str, int]): Summary of patterns found
            pattern_dates (Dict[str, List[str]]): Dates for each pattern
            
        Returns:
            str: Formatted analysis summary
        """
        total_patterns = sum(pattern_summary.values())
        total_candles = len(df)
        pattern_percentage = (total_patterns / total_candles * 100) if total_candles > 0 else 0
        
        summary = f"""
NIFTY Candlestick Pattern Analysis Summary
==========================================

Data Overview:
- Total candles analyzed: {total_candles}
- Total patterns found: {total_patterns}
- Pattern occurrence rate: {pattern_percentage:.2f}%

Pattern Breakdown:
"""
        
        for pattern, count in pattern_summary.items():
            if count > 0:
                summary += f"- {pattern}: {count} occurrences\n"
                if pattern in pattern_dates and pattern_dates[pattern]:
                    summary += f"  Dates: {', '.join(pattern_dates[pattern][:5])}"
                    if len(pattern_dates[pattern]) > 5:
                        summary += f" ... and {len(pattern_dates[pattern]) - 5} more"
                    summary += "\n"
        
        # Add price movement analysis
        if not df.empty:
            price_change = df['Close'].iloc[-1] - df['Close'].iloc[0]
            price_change_pct = (price_change / df['Close'].iloc[0]) * 100
            summary += f"""
Price Movement Analysis:
- Start price: {df['Close'].iloc[0]:.2f}
- End price: {df['Close'].iloc[-1]:.2f}
- Total change: {price_change:.2f} ({price_change_pct:+.2f}%)
- Highest price: {df['High'].max():.2f}
- Lowest price: {df['Low'].min():.2f}
"""
        
        return summary
    
    def run_complete_workflow(self) -> AnalysisResult:
        """
        Run the complete NIFTY data analysis workflow.
        
        Returns:
            AnalysisResult: Complete analysis results
        """
        logger.info("Starting complete NIFTY data analysis workflow")
        
        try:
            # Step 1: Fetch NIFTY data for 2025
            logger.info("Step 1: Fetching NIFTY data for 2025")
            csv_file_path = self.fetch_nifty_data_2025()
            
            if not csv_file_path:
                raise ValueError("Failed to fetch NIFTY data")
            
            # Step 2: Analyze candlestick patterns
            logger.info("Step 2: Analyzing candlestick patterns")
            result = self.analyze_candlestick_patterns(csv_file_path)
            
            # Step 3: Print summary
            logger.info("Step 3: Generating analysis summary")
            print("\n" + "="*60)
            print("NIFTY DATA ANALYSIS WORKFLOW COMPLETED")
            print("="*60)
            print(result.analysis_summary)
            print(f"\nDetailed results saved to: {result.output_file}")
            print("="*60)
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            raise

def main():
    """Main function to run the NIFTY data analysis workflow."""
    try:
        # Initialize workflow
        workflow = NiftyDataAnalysisWorkflow()
        
        # Run complete workflow
        result = workflow.run_complete_workflow()
        
        print(f"\n✅ Workflow completed successfully!")
        print(f"📊 Analysis results: {result.output_file}")
        
    except Exception as e:
        print(f"❌ Workflow failed: {str(e)}")
        logger.error(f"Workflow execution failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 