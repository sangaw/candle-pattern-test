#!/usr/bin/env python3
"""
Phase 1 Demo: Instrument Discovery
Demonstrates the AI agent's instrument discovery capabilities.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai_agent.orchestrator import InstrumentAnalysisOrchestrator

def demo_phase1():
    """Demonstrate Phase 1: Instrument Discovery."""
    print("🤖 AI Instrument Analysis - Phase 1 Demo")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = InstrumentAnalysisOrchestrator()
    
    # Demo test cases
    test_cases = [
        "I want to analyze NIFTY",
        "Show me BANKNIFTY futures",
        "Find RELIANCE stock",
        "I need TCS data for analysis",
        "Search for NSE equity instruments"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_input}")
        print("-" * 40)
        
        try:
            # Start analysis
            response = orchestrator.start_analysis(test_input)
            print(f"Response: {response}")
            
            # Show status
            status = orchestrator.get_current_status()
            print(f"Status: {status}")
            
            # Reset for next test
            orchestrator.reset_workflow()
            
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print()

def demo_interactive():
    """Demonstrate interactive workflow."""
    print("\n🔄 Interactive Demo")
    print("=" * 30)
    
    orchestrator = InstrumentAnalysisOrchestrator()
    
    # Simulate user interaction
    print("User: I want to analyze NIFTY")
    response1 = orchestrator.start_analysis("I want to analyze NIFTY")
    print(f"AI: {response1}")
    
    print("\nUser: 1,2")
    response2 = orchestrator.process_user_selection("1,2")
    print(f"AI: {response2}")
    
    status = orchestrator.get_current_status()
    print(f"\nFinal Status: {status}")

def main():
    """Main demo function."""
    try:
        # Demo 1: Basic functionality
        demo_phase1()
        
        # Demo 2: Interactive workflow
        demo_interactive()
        
        print("\n✅ Phase 1 Demo completed successfully!")
        print("\n💡 To try the interactive CLI, run:")
        print("   python src/ai_agent/interactive_cli.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 