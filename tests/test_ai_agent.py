#!/usr/bin/env python3
"""
Tests for AI Agent Phase 1: Instrument Discovery
"""
import pytest
import pandas as pd
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.ai_agent.base_agent.instrument_discovery import InstrumentDiscoveryAgent
from src.ai_agent.base_agent.orchestrator import InstrumentAnalysisOrchestrator

class TestInstrumentDiscoveryAgent:
    """Test cases for InstrumentDiscoveryAgent."""
    
    @pytest.fixture
    def sample_instruments_data(self):
        """Create sample instruments data for testing."""
        return pd.DataFrame({
            'instrument_token': [1, 2, 3, 4, 5],
            'tradingsymbol': ['NIFTY', 'BANKNIFTY', 'RELIANCE', 'TCS', 'INFY'],
            'name': ['NIFTY 50', 'NIFTY BANK', 'RELIANCE INDUSTRIES', 'TATA CONSULTANCY SERVICES', 'INFOSYS'],
            'exchange': ['NSE', 'NSE', 'NSE', 'NSE', 'NSE'],
            'instrument_type': ['EQ', 'EQ', 'EQ', 'EQ', 'EQ'],
            'segment': ['NSE', 'NSE', 'NSE', 'NSE', 'NSE'],
            'expiry': [None, None, None, None, None],
            'strike': [None, None, None, None, None],
            'lot_size': [50, 25, 1, 1, 1],
            'tick_size': [0.05, 0.05, 0.05, 0.05, 0.05]
        })
    
    @pytest.fixture
    def temp_csv_file(self, sample_instruments_data):
        """Create a temporary CSV file with sample data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_instruments_data.to_csv(f.name, index=False)
            yield f.name
        os.unlink(f.name)
    
    def test_init_with_valid_csv(self, temp_csv_file):
        """Test initialization with valid CSV file."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        assert agent.instruments_df is not None
        assert len(agent.instruments_df) == 5
        assert list(agent.instruments_df.columns) == [
            'instrument_token', 'tradingsymbol', 'name', 'exchange', 
            'instrument_type', 'segment', 'expiry', 'strike', 'lot_size', 'tick_size'
        ]
    
    def test_init_with_invalid_csv(self):
        """Test initialization with invalid CSV file."""
        with pytest.raises(Exception):
            InstrumentDiscoveryAgent("nonexistent_file.csv")
    
    def test_parse_user_input_basic(self, temp_csv_file):
        """Test basic user input parsing."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        # Test basic search
        result = agent.parse_user_input("I want to analyze NIFTY")
        assert result['original_input'] == "I want to analyze NIFTY"
        assert 'nifty' in result['search_terms']
        assert result['intent'] == 'analysis'
    
    def test_parse_user_input_with_exchange(self, temp_csv_file):
        """Test user input parsing with exchange preference."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        result = agent.parse_user_input("Show me NSE futures for NIFTY")
        assert 'NSE' in result['preferred_exchanges']
        assert 'FUT' in result['preferred_types']
        assert 'nifty' in result['search_terms']
    
    def test_parse_user_input_with_type(self, temp_csv_file):
        """Test user input parsing with instrument type preference."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        result = agent.parse_user_input("Find RELIANCE stock")
        assert 'EQ' in result['preferred_types']
        assert 'reliance' in result['search_terms']
    
    def test_search_instruments_exact_match(self, temp_csv_file):
        """Test instrument search with exact match."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        results = agent.search_instruments(['NIFTY'])
        assert len(results) > 0
        assert any('NIFTY' in str(name) for name in results['name'])
    
    def test_search_instruments_partial_match(self, temp_csv_file):
        """Test instrument search with partial match."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        results = agent.search_instruments(['RELIANCE'])
        assert len(results) > 0
        assert any('RELIANCE' in str(name) for name in results['name'])
    
    def test_search_instruments_no_match(self, temp_csv_file):
        """Test instrument search with no matches."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        results = agent.search_instruments(['XYZ123'])
        assert len(results) == 0
    
    def test_filter_and_rank_results(self, temp_csv_file):
        """Test filtering and ranking of results."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        # Create sample matches
        matches = agent.instruments_df.copy()
        parsed_input = {
            'preferred_exchanges': ['NSE'],
            'preferred_types': ['EQ'],
            'search_terms': ['NIFTY']
        }
        
        ranked_results = agent.filter_and_rank_results(matches, parsed_input)
        assert len(ranked_results) > 0
        assert 'relevance_score' in ranked_results.columns
        assert ranked_results['relevance_score'].max() > 0
    
    def test_present_options_to_user(self, temp_csv_file):
        """Test presentation of options to user."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        # Create sample ranked results
        ranked_results = agent.instruments_df.copy()
        ranked_results['relevance_score'] = [100, 90, 80, 70, 60]
        
        parsed_input = {'original_input': 'test query'}
        presentation = agent.present_options_to_user(ranked_results, parsed_input)
        
        assert 'found' in presentation.lower()
        assert 'instruments' in presentation.lower()
        assert 'relevant' in presentation.lower()
    
    def test_validate_user_selection_numbers(self, temp_csv_file):
        """Test user selection validation with numbers."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        ranked_results = agent.instruments_df.head(3)
        selection = "1,2"
        
        instruments, status = agent.validate_user_selection(selection, ranked_results)
        assert len(instruments) == 2
        assert 'Successfully' in status
    
    def test_validate_user_selection_names(self, temp_csv_file):
        """Test user selection validation with names."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        ranked_results = agent.instruments_df.head(3)
        selection = "NIFTY,RELIANCE"
        
        instruments, status = agent.validate_user_selection(selection, ranked_results)
        assert len(instruments) > 0
        assert 'Successfully' in status
    
    def test_validate_user_selection_invalid(self, temp_csv_file):
        """Test user selection validation with invalid input."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        ranked_results = agent.instruments_df.head(3)
        selection = "999,invalid"
        
        instruments, status = agent.validate_user_selection(selection, ranked_results)
        assert len(instruments) == 0
        assert 'No valid' in status
    
    def test_run_discovery_phase(self, temp_csv_file):
        """Test complete discovery phase."""
        agent = InstrumentDiscoveryAgent(temp_csv_file)
        
        user_input = "I want to analyze NIFTY"
        instruments, presentation = agent.run_discovery_phase(user_input)
        
        # Should return presentation for user selection
        assert isinstance(presentation, str)
        assert len(presentation) > 0

class TestInstrumentAnalysisOrchestrator:
    """Test cases for InstrumentAnalysisOrchestrator."""
    
    @pytest.fixture
    def sample_instruments_data(self):
        """Create sample instruments data for testing."""
        return pd.DataFrame({
            'instrument_token': [1, 2, 3, 4, 5],
            'tradingsymbol': ['NIFTY', 'BANKNIFTY', 'RELIANCE', 'TCS', 'INFY'],
            'name': ['NIFTY 50', 'NIFTY BANK', 'RELIANCE INDUSTRIES', 'TATA CONSULTANCY SERVICES', 'INFOSYS'],
            'exchange': ['NSE', 'NSE', 'NSE', 'NSE', 'NSE'],
            'instrument_type': ['EQ', 'EQ', 'EQ', 'EQ', 'EQ'],
            'segment': ['NSE', 'NSE', 'NSE', 'NSE', 'NSE'],
            'expiry': [None, None, None, None, None],
            'strike': [None, None, None, None, None],
            'lot_size': [50, 25, 1, 1, 1],
            'tick_size': [0.05, 0.05, 0.05, 0.05, 0.05]
        })
    
    @pytest.fixture
    def temp_csv_file(self, sample_instruments_data):
        """Create a temporary CSV file with sample data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            sample_instruments_data.to_csv(f.name, index=False)
            yield f.name
        os.unlink(f.name)
    
    def test_init(self, temp_csv_file):
        """Test orchestrator initialization."""
        orchestrator = InstrumentAnalysisOrchestrator(temp_csv_file)
        assert orchestrator.discovery_agent is not None
        assert orchestrator.selected_instruments == []
        assert orchestrator.current_phase == "idle"
    
    def test_start_analysis(self, temp_csv_file):
        """Test starting analysis workflow."""
        orchestrator = InstrumentAnalysisOrchestrator(temp_csv_file)
        
        user_input = "I want to analyze NIFTY"
        response = orchestrator.start_analysis(user_input)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert orchestrator.current_phase == "discovery"
    
    def test_process_user_selection(self, temp_csv_file):
        """Test processing user selection."""
        orchestrator = InstrumentAnalysisOrchestrator(temp_csv_file)
        
        # First start analysis
        orchestrator.start_analysis("I want to analyze NIFTY")
        
        # Then process selection
        selection = "1"
        response = orchestrator.process_user_selection(selection)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert orchestrator.current_phase == "data_collection"
    
    def test_get_current_status(self, temp_csv_file):
        """Test getting current status."""
        orchestrator = InstrumentAnalysisOrchestrator(temp_csv_file)
        
        status = orchestrator.get_current_status()
        assert isinstance(status, dict)
        assert 'current_phase' in status
        assert 'selected_instruments' in status
        assert 'analysis_results' in status
        assert 'timestamp' in status
    
    def test_reset_workflow(self, temp_csv_file):
        """Test resetting workflow."""
        orchestrator = InstrumentAnalysisOrchestrator(temp_csv_file)
        
        # Set some state
        orchestrator.selected_instruments = [{'test': 'data'}]
        orchestrator.current_phase = "discovery"
        
        # Reset
        orchestrator.reset_workflow()
        
        assert orchestrator.selected_instruments == []
        assert orchestrator.current_phase == "idle"
        assert orchestrator.analysis_results == {}

@pytest.fixture(scope="module")
def instruments_csv_fixture():
    os.makedirs("data", exist_ok=True)
    csv_path = "data/instruments_list_test.csv"
    df = pd.DataFrame([
        {"instrument_token": 1, "tradingsymbol": "NIFTYTEST", "name": "NIFTY", "exchange": "NSE", "instrument_type": "EQ", "segment": "NSE", "expiry": "", "strike": 0, "lot_size": 1, "tick_size": 0.05, "relevance_score": 100}
    ])
    df.to_csv(csv_path, index=False)
    yield csv_path
    os.remove(csv_path)

@pytest.mark.usefixtures("instruments_csv_fixture")
def test_integration_workflow(monkeypatch, instruments_csv_fixture):
    """Test complete integration workflow."""
    # Patch InstrumentDiscoveryAgent to use the test CSV
    from src.ai_agent.base_agent import instrument_discovery
    monkeypatch.setattr(instrument_discovery, "DEFAULT_CSV_PATH", instruments_csv_fixture)
    # Create a temporary orchestrator with the test CSV file
    orchestrator = InstrumentAnalysisOrchestrator(instruments_csv_path=instruments_csv_fixture)
    
    # Step 1: Start analysis
    response1 = orchestrator.start_analysis("I want to analyze NIFTY")
    assert "found" in response1.lower() or "instruments" in response1.lower()
    
    # Step 2: Process selection
    response2 = orchestrator.process_user_selection("1")
    assert "Selected instruments" in response2 or "Phase 2" in response2
    
    # Step 3: Check status
    status = orchestrator.get_current_status()
    assert status['current_phase'] in ['discovery', 'data_collection']
    assert status['selected_instruments'] >= 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 