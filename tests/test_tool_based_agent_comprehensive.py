#!/usr/bin/env python3
"""
Comprehensive Test for Tool-Based AI Agent
Tests all functionality with detailed logging.
"""
import os
import sys
import json
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_agent.tool_based_agent import ToolBasedAgent

# Configure comprehensive logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Create a detailed log file
log_file = os.path.join(log_dir, f'tool_based_agent_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_test_step(step_name: str, input_data: dict = None, output_data: dict = None, error: str = None):
    """Log test steps with input/output data."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'step': step_name,
        'input': input_data,
        'output': output_data,
        'error': error
    }
    
    logger.info(f"=== TEST STEP: {step_name} ===")
    if input_data:
        logger.info(f"Input: {json.dumps(input_data, indent=2, default=str)}")
    if output_data:
        logger.info(f"Output: {json.dumps(output_data, indent=2, default=str)}")
    if error:
        logger.error(f"Error: {error}")
    logger.info("=" * 50)

def test_tool_based_agent_comprehensive():
    """Comprehensive test of the tool-based AI agent."""
    print("🧪 Comprehensive Tool-Based AI Agent Test")
    print(f"📝 Detailed logs saved to: {log_file}")
    print("=" * 60)
    
    try:
        # Initialize agent
        logger.info("Initializing ToolBasedAgent")
        agent = ToolBasedAgent()
        
        # Test 1: Initial Status
        log_test_step("Initial Status", 
                     output_data=agent.get_status())
        
        # Test 2: Search for NIFTY futures
        search_input = "Show me NIFTY futures"
        log_test_step("Search Request", 
                     input_data={'user_input': search_input})
        
        result = agent.process_user_input(search_input)
        log_test_step("Search Response", 
                     output_data=result)
        
        # Test 3: Search for BANKNIFTY options
        search_input2 = "Find BANKNIFTY options"
        log_test_step("Search Request 2", 
                     input_data={'user_input': search_input2})
        
        result2 = agent.process_user_input(search_input2)
        log_test_step("Search Response 2", 
                     output_data=result2)
        
        # Test 4: Selection by number
        selection_input = "1"
        log_test_step("Selection by Number", 
                     input_data={'user_input': selection_input})
        
        result3 = agent.process_user_input(selection_input)
        log_test_step("Selection Response", 
                     output_data=result3)
        
        # Test 5: Selection by symbol
        selection_input2 = "NIFTY25AUGFUT"
        log_test_step("Selection by Symbol", 
                     input_data={'user_input': selection_input2})
        
        result4 = agent.process_user_input(selection_input2)
        log_test_step("Selection Response 2", 
                     output_data=result4)
        
        # Test 6: Data collection request
        data_input = "Fetch data for selected instruments"
        log_test_step("Data Collection Request", 
                     input_data={'user_input': data_input})
        
        result5 = agent.process_user_input(data_input)
        log_test_step("Data Collection Response", 
                     output_data=result5)
        
        # Test 7: Reset
        reset_input = "Reset workflow"
        log_test_step("Reset Request", 
                     input_data={'user_input': reset_input})
        
        result6 = agent.process_user_input(reset_input)
        log_test_step("Reset Response", 
                     output_data=result6)
        
        # Test 8: Final Status
        log_test_step("Final Status", 
                     output_data=agent.get_status())
        
        # Test 9: Invalid input
        invalid_input = "xyz123"
        log_test_step("Invalid Input", 
                     input_data={'user_input': invalid_input})
        
        result7 = agent.process_user_input(invalid_input)
        log_test_step("Invalid Input Response", 
                     output_data=result7)
        
        print("\n✅ Comprehensive test completed!")
        print(f"📊 Check detailed logs at: {log_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed with exception: {str(e)}")
        log_test_step("Test Failure", error=str(e))
        return False

def test_individual_tools():
    """Test individual tools with logging."""
    print("\n🔧 Testing Individual Tools")
    print("=" * 50)
    
    try:
        # Test search tool
        from ai_agent.tools.instrument_search_tool import search_instruments_tool
        
        search_params = {
            'search_terms': ['nifty', 'futures'],
            'preferred_exchanges': ['NFO'],
            'preferred_types': ['FUT'],
            'limit': 5
        }
        
        log_test_step("Search Tool Test", 
                     input_data=search_params)
        
        search_results = search_instruments_tool(**search_params)
        log_test_step("Search Tool Results", 
                     output_data=search_results)
        
        # Test data collection tool
        from ai_agent.tools.data_collection_tool import get_data_summary_tool
        
        if search_results['results']:
            summary = get_data_summary_tool(search_results['results'])
            log_test_step("Data Summary Tool", 
                         output_data=summary)
        
        print("✅ Individual tools test completed!")
        return True
        
    except Exception as e:
        logger.error(f"Individual tools test failed: {str(e)}")
        log_test_step("Individual Tools Failure", error=str(e))
        return False

def analyze_logs():
    """Analyze the test logs for issues."""
    print("\n📊 Analyzing Test Logs")
    print("=" * 50)
    
    try:
        with open(log_file, 'r') as f:
            log_content = f.read()
        
        # Look for common issues
        issues = []
        
        if "ERROR" in log_content:
            issues.append("❌ Errors found in logs")
        
        if "Object of type int64 is not JSON serializable" in log_content:
            issues.append("❌ JSON serialization issues with numpy types")
        
        if "ModuleNotFoundError" in log_content:
            issues.append("❌ Import/module issues")
        
        if "No valid instruments selected" in log_content:
            issues.append("⚠️  Instrument selection validation issues")
        
        if "No instruments selected" in log_content:
            issues.append("⚠️  State management issues")
        
        if issues:
            print("Issues found:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("✅ No major issues detected in logs")
        
        # Count successful vs failed steps
        success_count = log_content.count("Output:")
        error_count = log_content.count("Error:")
        
        print(f"\n📈 Test Statistics:")
        print(f"  Successful steps: {success_count}")
        print(f"  Error steps: {error_count}")
        print(f"  Success rate: {success_count/(success_count+error_count)*100:.1f}%" if (success_count+error_count) > 0 else "  Success rate: N/A")
        
    except Exception as e:
        print(f"❌ Error analyzing logs: {str(e)}")

if __name__ == '__main__':
    try:
        # Run comprehensive tests
        test_success = test_tool_based_agent_comprehensive()
        tools_success = test_individual_tools()
        
        # Analyze results
        analyze_logs()
        
        if test_success and tools_success:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n❌ Some tests failed. Check logs for details.")
        
        print(f"\n📝 Detailed logs available at: {log_file}")
        
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        print(f"❌ Test suite failed: {str(e)}") 