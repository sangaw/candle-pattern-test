#!/usr/bin/env python3
"""
Tool-Based AI Agent
An AI agent that uses Python tools to perform instrument analysis tasks.
"""
import logging
import re
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

from .tools.instrument_search_tool import search_instruments_tool, get_instrument_details_tool
from .tools.data_collection_tool import fetch_instrument_data_tool, fetch_multiple_instruments_tool

logger = logging.getLogger(__name__)

class ToolBasedAgent:
    """
    AI Agent that uses tools to perform tasks.
    """
    
    def __init__(self):
        """Initialize the tool-based agent."""
        self.conversation_history = []
        self.selected_instruments = []
        self.current_phase = "idle"
        self.last_search_results = []  # Store last search results for selection
        self.available_tools = {
            'search_instruments': search_instruments_tool,
            'get_instrument_details': get_instrument_details_tool,
            'fetch_instrument_data': fetch_instrument_data_tool,
            'fetch_multiple_instruments': fetch_multiple_instruments_tool
        }
    
    def process_user_input(self, user_input: str) -> Dict:
        """
        Process user input and determine appropriate action.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Dictionary with response and action taken
        """
        logger.info(f"Processing user input: {user_input}")
        
        # Add to conversation history
        self.conversation_history.append({
            'user': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Parse user intent
        intent = self._parse_user_intent(user_input)
        
        # Execute appropriate action based on intent
        if intent['type'] == 'search':
            return self._handle_search_intent(intent)
        elif intent['type'] == 'selection':
            return self._handle_selection_intent(intent)
        elif intent['type'] == 'data_collection':
            return self._handle_data_collection_intent(intent)
        elif intent['type'] == 'reset':
            return self._handle_reset_intent()
        else:
            return self._handle_unknown_intent(user_input)
    
    def _parse_user_intent(self, user_input: str) -> Dict:
        """
        Parse user input to determine intent and extract parameters.
        
        Args:
            user_input: User's input text
            
        Returns:
            Dictionary with intent type and parameters
        """
        input_lower = user_input.lower().strip()
        
        # Check for reset intent
        if any(word in input_lower for word in ['reset', 'start over', 'clear']):
            return {'type': 'reset'}
        
        # Check for data collection intent
        if any(word in input_lower for word in ['fetch', 'get data', 'collect data', 'download']):
            return {'type': 'data_collection'}
        
        # Check for selection (numbers or short instrument names)
        # Only treat as selection if we have previous search results
        if self._is_selection_input(user_input) and self.last_search_results:
            return {
                'type': 'selection',
                'selection': user_input,
                'original_input': user_input
            }
        
        # Default to search intent
        return {
            'type': 'search',
            'search_terms': self._extract_search_terms(input_lower),
            'preferred_exchanges': self._extract_exchanges(input_lower),
            'preferred_types': self._extract_instrument_types(input_lower),
            'original_input': user_input
        }
    
    def _extract_search_terms(self, input_lower: str) -> List[str]:
        """Extract search terms from user input."""
        # Remove common words
        common_words = {
            'i', 'want', 'to', 'analyze', 'check', 'look', 'at', 'the', 'a', 'an', 
            'and', 'or', 'but', 'in', 'on', 'at', 'for', 'of', 'with', 'by',
            'show', 'me', 'find', 'search', 'get', 'data', 'fetch', 'collect'
        }
        
        words = re.findall(r'\b\w+\b', input_lower)
        search_terms = [word for word in words if word not in common_words and len(word) > 2]
        
        return search_terms
    
    def _extract_exchanges(self, input_lower: str) -> List[str]:
        """Extract preferred exchanges from user input."""
        exchanges = []
        if 'nse' in input_lower:
            exchanges.append('NSE')
        if 'bse' in input_lower:
            exchanges.append('BSE')
        if 'nfo' in input_lower or 'futures' in input_lower:
            exchanges.append('NFO')
        return exchanges
    
    def _extract_instrument_types(self, input_lower: str) -> List[str]:
        """Extract preferred instrument types from user input."""
        types = []
        if any(word in input_lower for word in ['futures', 'fut']):
            types.append('FUT')
        if any(word in input_lower for word in ['options', 'ce', 'pe']):
            types.extend(['CE', 'PE'])
        if any(word in input_lower for word in ['equity', 'stock', 'eq']):
            types.append('EQ')
        return types
    
    def _is_selection_input(self, user_input: str) -> bool:
        """Check if input is a selection."""
        # Check for number patterns
        number_pattern = r'^\s*\d+(\s*[,\s]\s*\d+)*\s*$'
        if re.match(number_pattern, user_input):
            return True
        
        # Check for short instrument names
        words = user_input.split()
        if len(words) <= 3:
            instrument_names = ['nifty', 'banknifty', 'reliance', 'tcs', 'infy', 'hdfc', 'icici']
            return any(name in user_input.lower() for name in instrument_names)
        
        return False
    
    def _handle_search_intent(self, intent: Dict) -> Dict:
        """Handle search intent using the search tool."""
        logger.info("Handling search intent")
        
        try:
            # Use the search tool
            search_results = self.available_tools['search_instruments'](
                search_terms=intent['search_terms'],
                preferred_exchanges=intent['preferred_exchanges'],
                preferred_types=intent['preferred_types'],
                limit=10
            )
            
            # Store search results for selection
            self.last_search_results = search_results['results']
            
            # Format response
            response = self._format_search_results(search_results, intent['original_input'])
            
            # Update phase
            self.current_phase = "discovery"
            
            return {
                'success': True,
                'response': response,
                'action': 'search',
                'results': search_results,
                'phase': self.current_phase
            }
            
        except Exception as e:
            logger.error(f"Error in search: {str(e)}")
            return {
                'success': False,
                'response': f"Error performing search: {str(e)}",
                'action': 'search',
                'error': str(e)
            }
    
    def _handle_selection_intent(self, intent: Dict) -> Dict:
        """Handle selection intent."""
        logger.info("Handling selection intent")
        
        try:
            # Validate selection
            validated_instruments = self._validate_selection(intent['selection'])
            
            if not validated_instruments:
                return {
                    'success': False,
                    'response': "No valid instruments selected. Please try again.",
                    'action': 'selection'
                }
            
            # Update selected instruments
            self.selected_instruments = validated_instruments
            
            # Update phase
            self.current_phase = "data_collection"
            
            # Format response
            response = self._format_selection_results(validated_instruments)
            
            return {
                'success': True,
                'response': response,
                'action': 'selection',
                'selected_instruments': validated_instruments,
                'phase': self.current_phase
            }
            
        except Exception as e:
            logger.error(f"Error in selection: {str(e)}")
            return {
                'success': False,
                'response': f"Error processing selection: {str(e)}",
                'action': 'selection',
                'error': str(e)
            }
    
    def _handle_data_collection_intent(self, intent: Dict) -> Dict:
        """Handle data collection intent using the data collection tool."""
        logger.info("Handling data collection intent")
        
        if not self.selected_instruments:
            return {
                'success': False,
                'response': "No instruments selected. Please search and select instruments first.",
                'action': 'data_collection'
            }
        
        try:
            # Use the data collection tool
            collection_results = self.available_tools['fetch_multiple_instruments'](
                instruments=self.selected_instruments,
                days_back=30
            )
            
            # Format response
            response = self._format_data_collection_results(collection_results)
            
            return {
                'success': True,
                'response': response,
                'action': 'data_collection',
                'results': collection_results,
                'phase': self.current_phase
            }
            
        except Exception as e:
            logger.error(f"Error in data collection: {str(e)}")
            return {
                'success': False,
                'response': f"Error collecting data: {str(e)}",
                'action': 'data_collection',
                'error': str(e)
            }
    
    def _handle_reset_intent(self) -> Dict:
        """Handle reset intent."""
        logger.info("Handling reset intent")
        
        # Reset agent state
        self.selected_instruments = []
        self.current_phase = "idle"
        self.last_search_results = []  # Clear search results too
        
        return {
            'success': True,
            'response': "Workflow reset successfully. You can start a new analysis.",
            'action': 'reset',
            'phase': self.current_phase
        }
    
    def _handle_unknown_intent(self, user_input: str) -> Dict:
        """Handle unknown intent."""
        return {
            'success': False,
            'response': f"I'm not sure how to handle: '{user_input}'. Try asking me to search for instruments or select from results.",
            'action': 'unknown'
        }
    
    def _validate_selection(self, selection: str) -> List[Dict]:
        """Validate user selection against last search results."""
        if not self.last_search_results:
            return []
        
        # Handle number selections (1, 2, 3, etc.)
        if selection.isdigit():
            try:
                index = int(selection) - 1  # Convert to 0-based index
                if 0 <= index < len(self.last_search_results):
                    return [self.last_search_results[index]]
            except (ValueError, IndexError):
                pass
        
        # Handle comma-separated numbers (1,3,5)
        if ',' in selection:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected = []
                for index in indices:
                    if 0 <= index < len(self.last_search_results):
                        selected.append(self.last_search_results[index])
                return selected
            except (ValueError, IndexError):
                pass
        
        # Handle symbol selections (NIFTY25AUGFUT, etc.)
        selection_upper = selection.upper()
        for instrument in self.last_search_results:
            if (instrument['tradingsymbol'].upper() == selection_upper or 
                instrument['name'].upper() == selection_upper):
                return [instrument]
        
        # Try to get instrument details by symbol
        try:
            instrument = self.available_tools['get_instrument_details'](selection)
            if instrument:
                return [instrument]
        except:
            pass
        
        return []
    
    def _format_search_results(self, search_results: Dict, original_input: str) -> str:
        """Format search results for user display."""
        results = search_results['results']
        total_found = search_results['total_found']
        
        if not results:
            return f"I couldn't find any instruments matching '{original_input}'. Please try a different search term."
        
        response = f"I found {total_found} instruments related to '{original_input}'. Here are the top {len(results)} most relevant:\n\n"
        
        for i, instrument in enumerate(results, 1):
            name = instrument['name']
            symbol = instrument['tradingsymbol']
            exchange = instrument['exchange']
            instrument_type = instrument['instrument_type']
            
            response += f"{i}. {name} ({symbol})\n"
            response += f"   Exchange: {exchange} | Type: {instrument_type}\n\n"
        
        response += "Which instruments would you like to analyze? You can specify by number (e.g., '1,3') or by name (e.g., 'NIFTY, BANKNIFTY')."
        
        return response
    
    def _format_selection_results(self, instruments: List[Dict]) -> str:
        """Format selection results for user display."""
        response = f"Selected instruments for analysis:\n"
        
        for i, instrument in enumerate(instruments, 1):
            name = instrument['name']
            symbol = instrument['tradingsymbol']
            exchange = instrument['exchange']
            instrument_type = instrument['instrument_type']
            
            response += f"{i}. {name} ({symbol})\n"
            response += f"   Exchange: {exchange} | Type: {instrument_type}\n\n"
        
        response += "Phase 2: Data Collection - Ready!\n"
        response += "You can now fetch historical data for pattern analysis."
        
        return response
    
    def _format_data_collection_results(self, results: Dict) -> str:
        """Format data collection results for user display."""
        successful = results['successful_fetches']
        failed = results['failed_fetches']
        total = results['total_instruments']
        
        response = f"Data Collection Results:\n"
        response += f"✅ Successfully fetched data for {successful} instruments\n"
        response += f"❌ Failed to fetch data for {failed} instruments\n"
        response += f"📊 Total instruments processed: {total}\n\n"
        
        if successful > 0:
            response += "Data files have been saved with descriptive names.\n"
            response += "You can now proceed to pattern analysis."
        
        return response
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            'current_phase': self.current_phase,
            'selected_instruments': len(self.selected_instruments),
            'conversation_length': len(self.conversation_history),
            'last_search_results_count': len(self.last_search_results),
            'available_tools': list(self.available_tools.keys()),
            'timestamp': datetime.now().isoformat()
        } 