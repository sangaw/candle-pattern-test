#!/usr/bin/env python3
"""
Test Tool-Based AI Agent
Demonstrates the tool-based AI agent functionality.
"""
import os
import sys
import logging
import pytest
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_agent.tool_based_agent import ToolBasedAgent
from src.ai_agent.tool_based_agent.tools.instrument_search_tool import search_instruments_tool
from src.ai_agent.tool_based_agent.tools.data_collection_tool import get_data_summary_tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

def test_tool_based_agent():
    """Test the tool-based AI agent."""
    print("🧪 Testing Tool-Based AI Agent")
    print("=" * 50)
    
    # Initialize agent
    agent = ToolBasedAgent()
    
    # Test 1: Search for instruments
    print("\n1️⃣ Testing Instrument Search")
    print("-" * 30)
    
    search_input = "Show me NIFTY futures"
    print(f"User Input: {search_input}")
    
    result = agent.process_user_input(search_input)
    print(f"Success: {result['success']}")
    print(f"Action: {result['action']}")
    print(f"Phase: {result.get('phase', 'N/A')}")
    print(f"Response: {result['response'][:200]}...")
    
    # Test 2: Selection
    print("\n2️⃣ Testing Instrument Selection")
    print("-" * 30)
    
    selection_input = "1"
    print(f"User Input: {selection_input}")
    
    result = agent.process_user_input(selection_input)
    print(f"Success: {result['success']}")
    print(f"Action: {result['action']}")
    print(f"Phase: {result.get('phase', 'N/A')}")
    print(f"Response: {result['response'][:200]}...")
    
    # Test 3: Data Collection
    print("\n3️⃣ Testing Data Collection")
    print("-" * 30)
    
    data_input = "Fetch data for selected instruments"
    print(f"User Input: {data_input}")
    
    result = agent.process_user_input(data_input)
    print(f"Success: {result['success']}")
    print(f"Action: {result['action']}")
    print(f"Response: {result['response'][:200]}...")
    
    # Test 4: Reset
    print("\n4️⃣ Testing Reset")
    print("-" * 30)
    
    reset_input = "Reset workflow"
    print(f"User Input: {reset_input}")
    
    result = agent.process_user_input(reset_input)
    print(f"Success: {result['success']}")
    print(f"Action: {result['action']}")
    print(f"Phase: {result.get('phase', 'N/A')}")
    print(f"Response: {result['response']}")
    
    # Test 5: Agent Status
    print("\n5️⃣ Testing Agent Status")
    print("-" * 30)
    
    status = agent.get_status()
    print(f"Current Phase: {status['current_phase']}")
    print(f"Selected Instruments: {status['selected_instruments']}")
    print(f"Conversation Length: {status['conversation_length']}")
    print(f"Available Tools: {status['available_tools']}")
    
    print("\n✅ Tool-Based AI Agent Test Completed!")

def test_individual_tools(instruments_csv_fixture, monkeypatch):
    """Test individual tools."""
    print("\n🔧 Testing Individual Tools")
    print("=" * 50)
    
    # Patch InstrumentSearchTool to use the test CSV
    from src.ai_agent.tool_based_agent.tools import instrument_search_tool
    monkeypatch.setattr(instrument_search_tool, "DEFAULT_CSV_PATH", instruments_csv_fixture)
    
    # Test search tool
    print("\n1️⃣ Testing Search Tool")
    print("-" * 30)
    
    search_results = instrument_search_tool.search_instruments_tool(
        search_terms=['nifty'],
        preferred_exchanges=['NSE'],
        preferred_types=['EQ'],
        limit=5
    )
    print(f"Total Found: {search_results['total_found']}")
    print(f"Results: {len(search_results['results'])}")
    for i, instrument in enumerate(search_results['results'][:3], 1):
        print(f"  {i}. {instrument['name']} ({instrument['tradingsymbol']})")
    
    # Test data collection tool
    print("\n2️⃣ Testing Data Collection Tool")
    print("-" * 30)
    
    if search_results['results']:
        summary = get_data_summary_tool(search_results['results'])
        print(f"Summary: {summary['total_instruments']} instruments")
        print(f"Data Available: {len(summary['data_available'])}")
    
    print("\n✅ Individual Tools Test Completed!")

if __name__ == '__main__':
    try:
        test_tool_based_agent()
        test_individual_tools()
        
        print("\n🎉 All tests completed successfully!")
        print("\nTo run the web interface:")
        print("python src/ai_agent/tool_based_web_chatbot.py")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        print(f"❌ Test failed: {str(e)}") 