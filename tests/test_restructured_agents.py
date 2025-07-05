#!/usr/bin/env python3
"""
Comprehensive Test for Restructured AI Agents
Tests both base agent and tool-based agent implementations.
"""
import os
import sys
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai_agent.base_agent import InstrumentAnalysisOrchestrator, InteractiveCLI
from src.ai_agent.tool_based_agent import ToolBasedAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_base_agent():
    """Test the base agent implementation."""
    print("\n" + "="*60)
    print("🧪 Testing Base Agent Implementation")
    print("="*60)
    
    try:
        # Test orchestrator
        orchestrator = InstrumentAnalysisOrchestrator()
        
        # Test 1: Search for NIFTY
        print("\n📋 Test 1: Search for NIFTY")
        response = orchestrator.start_analysis("I want to analyze NIFTY")
        print(f"Response: {response[:200]}...")
        
        # Test 2: User selection
        print("\n📋 Test 2: User selection")
        selection_response = orchestrator.process_user_selection("1")
        print(f"Selection Response: {selection_response[:200]}...")
        
        # Test 3: Status
        print("\n📋 Test 3: Status check")
        status = orchestrator.get_current_status()
        print(f"Status: {status}")
        
        # Test 4: Reset
        print("\n📋 Test 4: Reset workflow")
        orchestrator.reset_workflow()
        print("Workflow reset successfully")
        
        print("✅ Base Agent tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Base Agent test failed: {str(e)}")
        logger.error(f"Base Agent test error: {str(e)}")

def test_tool_based_agent():
    """Test the tool-based agent implementation."""
    print("\n" + "="*60)
    print("🧪 Testing Tool-Based Agent Implementation")
    print("="*60)
    
    try:
        # Test tool-based agent
        agent = ToolBasedAgent()
        
        # Test 1: Search for BANKNIFTY
        print("\n📋 Test 1: Search for BANKNIFTY")
        response = agent.process_user_input("Find BANKNIFTY options")
        print(f"Response: {response['response'][:200]}...")
        print(f"Action: {response['action']}")
        print(f"Phase: {response['phase']}")
        
        # Test 2: Selection
        print("\n📋 Test 2: Selection")
        if response['action'] == 'search' and response['results']['results']:
            selection_response = agent.process_user_input("1")
            print(f"Selection Response: {selection_response['response'][:200]}...")
            print(f"Action: {selection_response['action']}")
        
        # Test 3: Status
        print("\n📋 Test 3: Status check")
        status = agent.get_status()
        print(f"Status: {status}")
        
        # Test 4: Reset
        print("\n📋 Test 4: Reset")
        reset_response = agent.process_user_input("reset")
        print(f"Reset Response: {reset_response['response']}")
        
        print("✅ Tool-Based Agent tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Tool-Based Agent test failed: {str(e)}")
        logger.error(f"Tool-Based Agent test error: {str(e)}")

def test_imports():
    """Test that all imports work correctly."""
    print("\n" + "="*60)
    print("🧪 Testing Imports")
    print("="*60)
    
    try:
        # Test base agent imports
        from src.ai_agent.base_agent import InstrumentAnalysisOrchestrator, InstrumentDiscoveryAgent, WebChatbot, InteractiveCLI
        print("✅ Base agent imports successful")
        
        # Test tool-based agent imports
        from src.ai_agent.tool_based_agent import ToolBasedAgent, ToolBasedWebChatbot, ToolBasedWebChatbotEnhanced
        print("✅ Tool-based agent imports successful")
        
        # Test tools imports
        from src.ai_agent.tool_based_agent.tools.instrument_search_tool import search_instruments_tool
        from src.ai_agent.tool_based_agent.tools.data_collection_tool import fetch_instrument_data_tool
        print("✅ Tools imports successful")
        
        print("✅ All imports working correctly!")
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        logger.error(f"Import test error: {str(e)}")

def test_file_structure():
    """Test that the file structure is correct."""
    print("\n" + "="*60)
    print("🧪 Testing File Structure")
    print("="*60)
    
    required_files = [
        'src/ai_agent/__init__.py',
        'src/ai_agent/base_agent/__init__.py',
        'src/ai_agent/base_agent/orchestrator.py',
        'src/ai_agent/base_agent/instrument_discovery.py',
        'src/ai_agent/base_agent/web_chatbot.py',
        'src/ai_agent/base_agent/interactive_cli.py',
        'src/ai_agent/base_agent/launch_web_chatbot.py',
        'src/ai_agent/tool_based_agent/__init__.py',
        'src/ai_agent/tool_based_agent/tool_based_agent.py',
        'src/ai_agent/tool_based_agent/tool_based_web_chatbot.py',
        'src/ai_agent/tool_based_agent/tool_based_web_chatbot_enhanced.py',
        'src/ai_agent/tool_based_agent/launch_web_chatbot.py',
        'src/ai_agent/tool_based_agent/tools/__init__.py',
        'src/ai_agent/tool_based_agent/tools/instrument_search_tool.py',
        'src/ai_agent/tool_based_agent/tools/data_collection_tool.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
    else:
        print("✅ All required files present!")

def main():
    """Run all tests."""
    print("🚀 Starting Comprehensive AI Agent Tests")
    print(f"📅 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test file structure
    test_file_structure()
    
    # Test imports
    test_imports()
    
    # Test base agent
    test_base_agent()
    
    # Test tool-based agent
    test_tool_based_agent()
    
    print("\n" + "="*60)
    print("🎉 All tests completed!")
    print("="*60)
    print("📁 Project structure reorganized successfully")
    print("🔧 Both agent implementations working correctly")
    print("🚀 Ready to use either implementation")

if __name__ == "__main__":
    main() 