#!/usr/bin/env python3
"""
AI Orchestrator for Instrument Analysis
Coordinates all phases of the instrument analysis workflow.
"""
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os

from .instrument_discovery import InstrumentDiscoveryAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InstrumentAnalysisOrchestrator:
    """
    Main orchestrator for the instrument analysis workflow.
    Coordinates all phases and manages the overall process.
    """
    
    def __init__(self, instruments_csv_path: str = "data/instruments_list_20250705_093603.csv"):
        """
        Initialize the orchestrator.
        
        Args:
            instruments_csv_path: Path to the instruments CSV file
        """
        self.instruments_csv_path = instruments_csv_path
        self.discovery_agent = InstrumentDiscoveryAgent(instruments_csv_path)
        self.selected_instruments = []
        self.analysis_results = {}
        self.current_phase = "idle"
        
    def start_analysis(self, user_input: str) -> str:
        """
        Start the instrument analysis workflow.
        
        Args:
            user_input: Natural language input from user
            
        Returns:
            Response message for the user
        """
        logger.info("Starting instrument analysis workflow")
        logger.info(f"User input: {user_input}")
        
        try:
            # Phase 1: Instrument Discovery
            self.current_phase = "discovery"
            logger.info("Phase 1: Instrument Discovery")
            
            instruments, presentation = self.discovery_agent.run_discovery_phase(user_input)
            
            if instruments:
                # If instruments were directly found, store them
                self.selected_instruments = instruments
                return self._format_discovery_results(instruments, presentation)
            else:
                # Present options to user for selection
                return presentation
                
        except Exception as e:
            logger.error(f"Error in analysis workflow: {str(e)}")
            return f"Error starting analysis: {str(e)}"
    
    def process_user_selection(self, user_selection: str) -> str:
        """
        Process user's instrument selection and proceed to next phase.
        
        Args:
            user_selection: User's selection input
            
        Returns:
            Response message for the user
        """
        logger.info(f"Processing user selection: {user_selection}")
        
        try:
            # Validate user selection
            validated_instruments, status = self.discovery_agent.validate_user_selection(
                user_selection, 
                self.discovery_agent.instruments_df.head(10)  # Use top 10 from discovery
            )
            
            if not validated_instruments:
                return status
            
            self.selected_instruments = validated_instruments
            
            # Proceed to Phase 2: Data Collection
            return self._start_data_collection_phase()
            
        except Exception as e:
            logger.error(f"Error processing user selection: {str(e)}")
            return f"Error processing selection: {str(e)}"
    
    def _start_data_collection_phase(self) -> str:
        """
        Start Phase 2: Data Collection.
        
        Returns:
            Response message for the user
        """
        logger.info("Phase 2: Data Collection")
        self.current_phase = "data_collection"
        
        try:
            # Show both name and trading symbol for clarity
            response = f"Selected instruments for analysis:\n"
            for i, instrument in enumerate(self.selected_instruments, 1):
                name = instrument['name']
                symbol = instrument['tradingsymbol']
                exchange = instrument['exchange']
                instrument_type = instrument['instrument_type']
                
                response += f"{i}. {name} ({symbol})\n"
                response += f"   Exchange: {exchange} | Type: {instrument_type}\n\n"
            
            response += f"Phase 2: Data Collection - Coming soon!\n"
            response += f"This phase will fetch historical candle data for pattern analysis."
            
            return response
            
        except Exception as e:
            logger.error(f"Error in data collection phase: {str(e)}")
            return f"Error in data collection: {str(e)}"
    
    def _format_discovery_results(self, instruments: List[Dict], presentation: str) -> str:
        """
        Format discovery results for user presentation.
        
        Args:
            instruments: List of discovered instruments
            presentation: Original presentation message
            
        Returns:
            Formatted response
        """
        if not instruments:
            return presentation
        
        response = f"Direct matches found for your query:\n\n"
        
        for i, instrument in enumerate(instruments, 1):
            response += f"{i}. {instrument['name']} ({instrument['tradingsymbol']})\n"
            response += f"   Exchange: {instrument['exchange']} | Type: {instrument['instrument_type']}\n\n"
        
        response += "Proceeding to data collection phase..."
        return response
    
    def get_current_status(self) -> Dict:
        """
        Get current status of the analysis workflow.
        
        Returns:
            Dictionary with current status information
        """
        return {
            'current_phase': self.current_phase,
            'selected_instruments': len(self.selected_instruments),
            'analysis_results': len(self.analysis_results),
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_workflow(self):
        """Reset the workflow to initial state."""
        logger.info("Resetting workflow")
        self.selected_instruments = []
        self.analysis_results = {}
        self.current_phase = "idle"

def main():
    """Test the orchestrator."""
    orchestrator = InstrumentAnalysisOrchestrator()
    
    # Test the workflow
    print("Testing Instrument Analysis Orchestrator")
    print("=" * 50)
    
    # Test case 1: Direct search
    test_input = "I want to analyze NIFTY"
    print(f"\nTest 1: {test_input}")
    response = orchestrator.start_analysis(test_input)
    print(f"Response: {response}")
    
    # Test case 2: User selection
    print(f"\nTest 2: User selection")
    selection = "1,2"
    response = orchestrator.process_user_selection(selection)
    print(f"Response: {response}")
    
    # Show status
    status = orchestrator.get_current_status()
    print(f"\nStatus: {status}")

if __name__ == "__main__":
    main() 