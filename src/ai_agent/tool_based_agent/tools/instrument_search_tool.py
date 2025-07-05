#!/usr/bin/env python3
"""
Instrument Search Tool
A tool for searching and discovering financial instruments.
"""
import pandas as pd
import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_CSV_PATH = "data/instruments_list_20250705_093603.csv"

class InstrumentSearchTool:
    """
    Tool for searching financial instruments.
    """
    
    def __init__(self, instruments_csv_path: str = None):
        """Initialize the instrument search tool."""
        self.instruments_csv_path = instruments_csv_path or DEFAULT_CSV_PATH
        self.instruments_df = None
        self.load_instruments_data()
    
    def load_instruments_data(self):
        """Load instruments data."""
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
    
    def search_instruments(self, search_terms: List[str], 
                          preferred_exchanges: List[str] = None,
                          preferred_types: List[str] = None,
                          limit: int = 10) -> Dict:
        """
        Search for instruments based on criteria.
        
        Args:
            search_terms: List of search terms
            preferred_exchanges: Preferred exchanges (NSE, BSE, NFO)
            preferred_types: Preferred instrument types (EQ, FUT, CE, PE)
            limit: Maximum number of results
            
        Returns:
            Dictionary with search results and metadata
        """
        logger.info(f"Searching instruments with terms: {search_terms}")
        
        if self.instruments_df is None:
            raise ValueError("Instruments data not loaded")
        
        # Create search patterns
        search_patterns = []
        for term in search_terms:
            search_patterns.extend([f"^{term}$", term, f"\\b{term}\\b"])
        
        # Search in name and tradingsymbol columns
        matches = []
        for pattern in search_patterns:
            try:
                name_matches = self.instruments_df[
                    self.instruments_df['name'].str.contains(pattern, case=False, na=False)
                ]
                matches.append(name_matches)
                
                symbol_matches = self.instruments_df[
                    self.instruments_df['tradingsymbol'].str.contains(pattern, case=False, na=False)
                ]
                matches.append(symbol_matches)
                
            except Exception as e:
                logger.warning(f"Error with pattern {pattern}: {str(e)}")
                continue
        
        if matches:
            combined_matches = pd.concat(matches, ignore_index=True)
            combined_matches = combined_matches.drop_duplicates(subset=['instrument_token'])
        else:
            combined_matches = pd.DataFrame()
        
        # Apply filters
        if preferred_exchanges:
            combined_matches = combined_matches[
                combined_matches['exchange'].isin(preferred_exchanges)
            ]
        
        if preferred_types:
            combined_matches = combined_matches[
                combined_matches['instrument_type'].isin(preferred_types)
            ]
        
        # Calculate relevance scores
        combined_matches = self._calculate_relevance_scores(combined_matches, search_terms)
        
        # Sort and limit results
        combined_matches = combined_matches.sort_values('relevance_score', ascending=False).head(limit)
        
        # Convert to list of dictionaries
        results = []
        for _, row in combined_matches.iterrows():
            results.append({
                'instrument_token': to_native(row['instrument_token']),
                'tradingsymbol': to_native(row['tradingsymbol']),
                'name': to_native(row['name']),
                'exchange': to_native(row['exchange']),
                'instrument_type': to_native(row['instrument_type']),
                'segment': to_native(row['segment']),
                'expiry': to_native(row['expiry']),
                'strike': to_native(row['strike']),
                'lot_size': to_native(row['lot_size']),
                'tick_size': to_native(row['tick_size']),
                'relevance_score': to_native(row['relevance_score'])
            })
        
        return {
            'results': results,
            'total_found': len(combined_matches),
            'search_terms': search_terms,
            'filters_applied': {
                'exchanges': preferred_exchanges or [],
                'types': preferred_types or []
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_relevance_scores(self, df: pd.DataFrame, search_terms: List[str]) -> pd.DataFrame:
        """Calculate relevance scores for search results."""
        df = df.copy()
        df['relevance_score'] = 0.0
        
        for idx, row in df.iterrows():
            score = 0.0
            
            name_lower = str(row['name']).lower()
            symbol_lower = str(row['tradingsymbol']).lower()
            
            for term in search_terms:
                term_lower = term.lower()
                
                # Exact matches
                if name_lower == term_lower:
                    score += 100
                elif symbol_lower == term_lower:
                    score += 90
                
                # Partial matches
                elif name_lower.startswith(term_lower):
                    score += 80
                elif symbol_lower.startswith(term_lower):
                    score += 70
                elif term_lower in name_lower:
                    score += 50
                elif term_lower in symbol_lower:
                    score += 40
                elif re.search(rf'\b{term_lower}\b', name_lower):
                    score += 60
                elif re.search(rf'\b{term_lower}\b', symbol_lower):
                    score += 50
            
            # Bonuses
            if row['instrument_type'] == 'EQ':
                score += 10
            if row['exchange'] == 'NSE':
                score += 5
            if any(index in str(row['name']).upper() for index in ['NIFTY', 'SENSEX', 'BANKNIFTY']):
                score += 20
            
            df.at[idx, 'relevance_score'] = score
        
        return df
    
    def get_instrument_by_token(self, instrument_token: int) -> Optional[Dict]:
        """Get instrument details by token."""
        if self.instruments_df is None:
            return None
        
        match = self.instruments_df[self.instruments_df['instrument_token'] == instrument_token]
        if not match.empty:
            row = match.iloc[0]
            return {
                'instrument_token': to_native(row['instrument_token']),
                'tradingsymbol': to_native(row['tradingsymbol']),
                'name': to_native(row['name']),
                'exchange': to_native(row['exchange']),
                'instrument_type': to_native(row['instrument_type']),
                'segment': to_native(row['segment']),
                'expiry': to_native(row['expiry']),
                'strike': to_native(row['strike']),
                'lot_size': to_native(row['lot_size']),
                'tick_size': to_native(row['tick_size'])
            }
        return None
    
    def get_instrument_by_symbol(self, symbol: str) -> Optional[Dict]:
        """Get instrument details by trading symbol."""
        if self.instruments_df is None:
            return None
        
        match = self.instruments_df[
            self.instruments_df['tradingsymbol'].str.lower() == symbol.lower()
        ]
        if not match.empty:
            row = match.iloc[0]
            return {
                'instrument_token': to_native(row['instrument_token']),
                'tradingsymbol': to_native(row['tradingsymbol']),
                'name': to_native(row['name']),
                'exchange': to_native(row['exchange']),
                'instrument_type': to_native(row['instrument_type']),
                'segment': to_native(row['segment']),
                'expiry': to_native(row['expiry']),
                'strike': to_native(row['strike']),
                'lot_size': to_native(row['lot_size']),
                'tick_size': to_native(row['tick_size'])
            }
        return None

def to_native(val):
    if isinstance(val, (np.integer,)):
        return int(val)
    if isinstance(val, (np.floating,)):
        return float(val)
    if isinstance(val, (np.bool_)):
        return bool(val)
    if isinstance(val, (np.ndarray,)):
        return val.tolist()
    return val

# Tool function for the AI agent
def search_instruments_tool(search_terms: List[str], 
                           preferred_exchanges: List[str] = None,
                           preferred_types: List[str] = None,
                           limit: int = 10,
                           instruments_csv_path: str = None) -> Dict:
    """
    Tool function for searching instruments.
    
    Args:
        search_terms: List of search terms
        preferred_exchanges: Preferred exchanges
        preferred_types: Preferred instrument types
        limit: Maximum number of results
        
    Returns:
        Search results dictionary
    """
    tool = InstrumentSearchTool(instruments_csv_path)
    return tool.search_instruments(search_terms, preferred_exchanges, preferred_types, limit)

def get_instrument_details_tool(identifier: str) -> Optional[Dict]:
    """
    Tool function for getting instrument details.
    
    Args:
        identifier: Instrument token (int) or symbol (str)
        
    Returns:
        Instrument details dictionary
    """
    tool = InstrumentSearchTool()
    
    # Try as token first
    try:
        token = int(identifier)
        return tool.get_instrument_by_token(token)
    except ValueError:
        # Try as symbol
        return tool.get_instrument_by_symbol(identifier) 