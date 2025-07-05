#!/usr/bin/env python3
"""
Phase 1: Instrument Discovery Module
Handles instrument search, filtering, ranking, and user interaction.
"""
import pandas as pd
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DEFAULT_CSV_PATH = "data/instruments_list_20250705_093603.csv"

class InstrumentDiscoveryAgent:
    """
    AI Agent for Phase 1: Instrument Discovery
    Handles user input parsing, instrument search, filtering, and ranking.
    """
    
    def __init__(self, instruments_csv_path: str = None):
        """
        Initialize the instrument discovery agent.
        
        Args:
            instruments_csv_path: Path to the instruments CSV file
        """
        self.instruments_csv_path = instruments_csv_path or DEFAULT_CSV_PATH
        self.instruments_df = None
        self.load_instruments_data()
        
    def load_instruments_data(self):
        """Load and prepare instruments data for searching."""
        try:
            logger.info(f"Loading instruments data from {self.instruments_csv_path}")
            self.instruments_df = pd.read_csv(self.instruments_csv_path)
            
            # Clean and prepare data
            self.instruments_df['name'] = self.instruments_df['name'].fillna('')
            self.instruments_df['tradingsymbol'] = self.instruments_df['tradingsymbol'].fillna('')
            
            logger.info(f"Loaded {len(self.instruments_df)} instruments")
            
        except Exception as e:
            logger.error(f"Error loading instruments data: {str(e)}")
            raise
    
    def parse_user_input(self, user_input: str) -> Dict:
        """
        Parse and understand user input for instrument search.
        
        Args:
            user_input: Natural language input from user
            
        Returns:
            Dictionary with parsed information
        """
        logger.info(f"Parsing user input: {user_input}")
        
        # Convert to lowercase for better matching
        input_lower = user_input.lower()
        
        # Extract key terms
        parsed = {
            'original_input': user_input,
            'search_terms': [],
            'intent': 'analysis',
            'preferred_exchanges': [],
            'preferred_types': []
        }
        
        # Extract search terms (remove common words)
        common_words = {'i', 'want', 'to', 'analyze', 'check', 'look', 'at', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b\w+\b', input_lower)
        search_terms = [word for word in words if word not in common_words and len(word) > 2]
        
        parsed['search_terms'] = search_terms
        
        # Detect intent
        if any(word in input_lower for word in ['analyze', 'analysis', 'check', 'look']):
            parsed['intent'] = 'analysis'
        elif any(word in input_lower for word in ['buy', 'sell', 'trade']):
            parsed['intent'] = 'trading'
        elif any(word in input_lower for word in ['monitor', 'watch', 'track']):
            parsed['intent'] = 'monitoring'
        
        # Detect exchange preferences
        if 'nse' in input_lower:
            parsed['preferred_exchanges'].append('NSE')
        if 'bse' in input_lower:
            parsed['preferred_exchanges'].append('BSE')
        if 'nfo' in input_lower or 'futures' in input_lower:
            parsed['preferred_exchanges'].append('NFO')
        
        # Detect instrument type preferences
        if any(word in input_lower for word in ['futures', 'fut']):
            parsed['preferred_types'].append('FUT')
        if any(word in input_lower for word in ['options', 'ce', 'pe']):
            parsed['preferred_types'].extend(['CE', 'PE'])
        if any(word in input_lower for word in ['equity', 'stock', 'eq']):
            parsed['preferred_types'].append('EQ')
        
        logger.info(f"Parsed input: {parsed}")
        return parsed
    
    def search_instruments(self, search_terms: List[str], limit: int = 15) -> pd.DataFrame:
        """
        Search instruments by name, symbol, or description.
        
        Args:
            search_terms: List of search terms
            limit: Maximum number of results
            
        Returns:
            DataFrame with matching instruments
        """
        logger.info(f"Searching instruments with terms: {search_terms}")
        
        if self.instruments_df is None:
            raise ValueError("Instruments data not loaded")
        
        # Create search patterns
        search_patterns = []
        for term in search_terms:
            # Exact match
            search_patterns.append(f"^{term}$")
            # Contains match
            search_patterns.append(term)
            # Word boundary match
            search_patterns.append(f"\\b{term}\\b")
        
        # Search in name and tradingsymbol columns
        matches = []
        for pattern in search_patterns:
            try:
                # Search in name column
                name_matches = self.instruments_df[
                    self.instruments_df['name'].str.contains(pattern, case=False, na=False)
                ]
                matches.append(name_matches)
                
                # Search in tradingsymbol column
                symbol_matches = self.instruments_df[
                    self.instruments_df['tradingsymbol'].str.contains(pattern, case=False, na=False)
                ]
                matches.append(symbol_matches)
                
            except Exception as e:
                logger.warning(f"Error with pattern {pattern}: {str(e)}")
                continue
        
        if matches:
            # Combine all matches and remove duplicates
            combined_matches = pd.concat(matches, ignore_index=True)
            combined_matches = combined_matches.drop_duplicates(subset=['instrument_token'])
        else:
            combined_matches = pd.DataFrame()
        
        logger.info(f"Found {len(combined_matches)} initial matches")
        return combined_matches
    
    def filter_and_rank_results(self, matches_df: pd.DataFrame, parsed_input: Dict) -> pd.DataFrame:
        """
        Filter and rank search results based on relevance and preferences.
        
        Args:
            matches_df: DataFrame with initial matches
            parsed_input: Parsed user input with preferences
            
        Returns:
            DataFrame with filtered and ranked results
        """
        logger.info("Filtering and ranking results")
        
        if matches_df.empty:
            return matches_df
        
        # Apply exchange filter if specified
        if parsed_input['preferred_exchanges']:
            matches_df = matches_df[
                matches_df['exchange'].isin(parsed_input['preferred_exchanges'])
            ]
            logger.info(f"After exchange filter: {len(matches_df)} matches")
        
        # Apply instrument type filter if specified
        if parsed_input['preferred_types']:
            matches_df = matches_df[
                matches_df['instrument_type'].isin(parsed_input['preferred_types'])
            ]
            logger.info(f"After type filter: {len(matches_df)} matches")
        
        # Calculate relevance scores
        matches_df = self._calculate_relevance_scores(matches_df, parsed_input)
        
        # Sort by relevance score
        matches_df = matches_df.sort_values('relevance_score', ascending=False)
        
        return matches_df
    
    def _calculate_relevance_scores(self, df: pd.DataFrame, parsed_input: Dict) -> pd.DataFrame:
        """
        Calculate relevance scores for search results.
        
        Args:
            df: DataFrame with matches
            parsed_input: Parsed user input
            
        Returns:
            DataFrame with relevance scores
        """
        df = df.copy()
        df['relevance_score'] = 0.0
        
        search_terms = parsed_input['search_terms']
        
        for idx, row in df.iterrows():
            score = 0.0
            
            # Name matching
            name_lower = str(row['name']).lower()
            symbol_lower = str(row['tradingsymbol']).lower()
            
            for term in search_terms:
                term_lower = term.lower()
                
                # Exact match in name (highest score)
                if name_lower == term_lower:
                    score += 100
                # Exact match in symbol
                elif symbol_lower == term_lower:
                    score += 90
                # Starts with term in name
                elif name_lower.startswith(term_lower):
                    score += 80
                # Starts with term in symbol
                elif symbol_lower.startswith(term_lower):
                    score += 70
                # Contains term in name
                elif term_lower in name_lower:
                    score += 50
                # Contains term in symbol
                elif term_lower in symbol_lower:
                    score += 40
                # Word boundary match in name
                elif re.search(rf'\b{term_lower}\b', name_lower):
                    score += 60
                # Word boundary match in symbol
                elif re.search(rf'\b{term_lower}\b', symbol_lower):
                    score += 50
            
            # Bonus for popular instruments
            if row['instrument_type'] == 'EQ':
                score += 10
            if row['exchange'] == 'NSE':
                score += 5
            
            # Bonus for index instruments
            if any(index in str(row['name']).upper() for index in ['NIFTY', 'SENSEX', 'BANKNIFTY']):
                score += 20
            
            df.at[idx, 'relevance_score'] = score
        
        return df
    
    def present_options_to_user(self, ranked_results: pd.DataFrame, parsed_input: Dict) -> str:
        """
        Present ranked options to user in a friendly format.
        
        Args:
            ranked_results: DataFrame with ranked results
            parsed_input: Parsed user input
            
        Returns:
            Formatted string for user presentation
        """
        logger.info("Presenting options to user")
        
        if ranked_results.empty:
            return f"I couldn't find any instruments matching '{parsed_input['original_input']}'. Please try a different search term."
        
        # Take top results
        top_results = ranked_results.head(10)
        
        # Format the presentation
        presentation = f"I found {len(ranked_results)} instruments related to '{parsed_input['original_input']}'. Here are the top {len(top_results)} most relevant:\n\n"
        
        for i, (idx, row) in enumerate(top_results.iterrows(), 1):
            name = row['name']
            symbol = row['tradingsymbol']
            exchange = row['exchange']
            instrument_type = row['instrument_type']
            token = row['instrument_token']
            
            # Format instrument type for display
            type_display = {
                'EQ': 'Equity',
                'FUT': 'Futures',
                'CE': 'Call Option',
                'PE': 'Put Option'
            }.get(instrument_type, instrument_type)
            
            presentation += f"{i}. {name} ({symbol})\n"
            presentation += f"   Exchange: {exchange} | Type: {type_display} | Token: {token}\n\n"
        
        presentation += "Which instruments would you like to analyze? You can specify by number (e.g., '1,3') or by name (e.g., 'NIFTY, BANKNIFTY')."
        
        return presentation
    
    def validate_user_selection(self, user_selection: str, ranked_results: pd.DataFrame) -> Tuple[List[Dict], str]:
        """
        Validate user's instrument selection.
        
        Args:
            user_selection: User's selection input
            ranked_results: DataFrame with ranked results
            
        Returns:
            Tuple of (validated_instruments, status_message)
        """
        logger.info(f"Validating user selection: {user_selection}")
        
        if ranked_results.empty:
            return [], "No instruments available for selection."
        
        top_results = ranked_results.head(10)
        validated_instruments = []
        
        # Parse selection (numbers or names)
        selection_parts = [part.strip() for part in user_selection.split(',')]
        
        for part in selection_parts:
            try:
                # Try as number
                if part.isdigit():
                    num = int(part)
                    if 1 <= num <= len(top_results):
                        selected_row = top_results.iloc[num - 1]
                        validated_instruments.append({
                            'name': selected_row['name'],
                            'tradingsymbol': selected_row['tradingsymbol'],
                            'exchange': selected_row['exchange'],
                            'instrument_type': selected_row['instrument_type'],
                            'instrument_token': selected_row['instrument_token']
                        })
                    else:
                        logger.warning(f"Invalid selection number: {num}")
                else:
                    # Try as name/symbol with more flexible matching
                    part_lower = part.lower()
                    
                    # First try exact matches
                    exact_matches = top_results[
                        (top_results['name'].str.lower() == part_lower) |
                        (top_results['tradingsymbol'].str.lower() == part_lower)
                    ]
                    
                    if not exact_matches.empty:
                        for _, row in exact_matches.iterrows():
                            validated_instruments.append({
                                'name': row['name'],
                                'tradingsymbol': row['tradingsymbol'],
                                'exchange': row['exchange'],
                                'instrument_type': row['instrument_type'],
                                'instrument_token': row['instrument_token']
                            })
                    else:
                        # Try partial matches
                        partial_matches = top_results[
                            (top_results['name'].str.contains(part, case=False, na=False)) |
                            (top_results['tradingsymbol'].str.contains(part, case=False, na=False))
                        ]
                        
                        if not partial_matches.empty:
                            for _, row in partial_matches.iterrows():
                                validated_instruments.append({
                                    'name': row['name'],
                                    'tradingsymbol': row['tradingsymbol'],
                                    'exchange': row['exchange'],
                                    'instrument_type': row['instrument_type'],
                                    'instrument_token': row['instrument_token']
                                })
                        else:
                            # Try searching in the full dataset for this specific symbol
                            full_matches = self.instruments_df[
                                (self.instruments_df['name'].str.contains(part, case=False, na=False)) |
                                (self.instruments_df['tradingsymbol'].str.contains(part, case=False, na=False))
                            ]
                            
                            if not full_matches.empty:
                                # Take the first match from full dataset
                                row = full_matches.iloc[0]
                                validated_instruments.append({
                                    'name': row['name'],
                                    'tradingsymbol': row['tradingsymbol'],
                                    'exchange': row['exchange'],
                                    'instrument_type': row['instrument_type'],
                                    'instrument_token': row['instrument_token']
                                })
                                logger.info(f"Found match in full dataset: {row['tradingsymbol']}")
                            else:
                                logger.warning(f"No match found for: {part}")
                        
            except Exception as e:
                logger.error(f"Error processing selection part '{part}': {str(e)}")
        
        # Remove duplicates
        unique_instruments = []
        seen_tokens = set()
        for instrument in validated_instruments:
            if instrument['instrument_token'] not in seen_tokens:
                unique_instruments.append(instrument)
                seen_tokens.add(instrument['instrument_token'])
        
        if unique_instruments:
            status = f"Successfully validated {len(unique_instruments)} instruments for analysis."
        else:
            status = "No valid instruments selected. Please try again."
        
        logger.info(f"Validated {len(unique_instruments)} instruments")
        return unique_instruments, status
    
    def run_discovery_phase(self, user_input: str) -> Tuple[List[Dict], str]:
        """
        Run the complete Phase 1: Instrument Discovery.
        
        Args:
            user_input: Natural language input from user
            
        Returns:
            Tuple of (validated_instruments, presentation_message)
        """
        logger.info("Starting Phase 1: Instrument Discovery")
        
        try:
            # Step 1: Parse user input
            parsed_input = self.parse_user_input(user_input)
            
            # Step 2: Search instruments
            matches = self.search_instruments(parsed_input['search_terms'])
            
            # Step 3: Filter and rank results
            ranked_results = self.filter_and_rank_results(matches, parsed_input)
            
            # Step 4: Present options to user
            presentation = self.present_options_to_user(ranked_results, parsed_input)
            
            logger.info("Phase 1 completed successfully")
            return [], presentation
            
        except Exception as e:
            logger.error(f"Error in discovery phase: {str(e)}")
            return [], f"Error during instrument discovery: {str(e)}"

def main():
    """Test the instrument discovery agent."""
    agent = InstrumentDiscoveryAgent()
    
    # Test cases
    test_inputs = [
        "I want to analyze NIFTY",
        "Show me BANKNIFTY instruments",
        "I need RELIANCE stock data",
        "Find NSE futures for NIFTY"
    ]
    
    for test_input in test_inputs:
        print(f"\n{'='*50}")
        print(f"Testing: {test_input}")
        print(f"{'='*50}")
        
        instruments, presentation = agent.run_discovery_phase(test_input)
        print(presentation)

if __name__ == "__main__":
    main() 