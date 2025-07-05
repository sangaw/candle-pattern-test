#!/usr/bin/env python3
"""
Interactive CLI for testing the AI Instrument Analysis Orchestrator.
"""
import sys
import os
import logging
from typing import Optional

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .orchestrator import InstrumentAnalysisOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class InteractiveCLI:
    """
    Interactive command-line interface for the AI orchestrator.
    """
    
    def __init__(self):
        """Initialize the CLI interface."""
        self.orchestrator = InstrumentAnalysisOrchestrator()
        self.running = True
        
    def print_banner(self):
        """Print the application banner."""
        print("\n" + "="*60)
        print("🤖 AI Instrument Analysis Orchestrator")
        print("="*60)
        print("Phase 1: Instrument Discovery")
        print("Type 'help' for commands, 'quit' to exit")
        print("="*60 + "\n")
    
    def print_help(self):
        """Print help information."""
        print("\n📋 Available Commands:")
        print("  analyze <query>     - Start instrument analysis with natural language query")
        print("  select <numbers>    - Select instruments by number (e.g., 'select 1,3')")
        print("  status             - Show current workflow status")
        print("  reset              - Reset the workflow")
        print("  help               - Show this help message")
        print("  quit               - Exit the application")
        print("\n💡 Examples:")
        print("  analyze I want to analyze NIFTY")
        print("  analyze Show me BANKNIFTY futures")
        print("  analyze Find RELIANCE stock")
        print("  select 1,2")
        print()
    
    def process_command(self, command: str) -> bool:
        """
        Process a user command.
        
        Args:
            command: User input command
            
        Returns:
            True if should continue, False if should quit
        """
        command = command.strip()
        
        if not command:
            return True
        
        parts = command.split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        try:
            if cmd == 'quit' or cmd == 'exit':
                print("👋 Goodbye!")
                return False
                
            elif cmd == 'help':
                self.print_help()
                
            elif cmd == 'analyze':
                if not args:
                    print("❌ Please provide a query. Example: analyze NIFTY")
                    return True
                
                print(f"🔍 Analyzing: {args}")
                response = self.orchestrator.start_analysis(args)
                print(f"\n{response}")
                
            elif cmd == 'select':
                if not args:
                    print("❌ Please provide selection numbers. Example: select 1,2")
                    return True
                
                print(f"✅ Processing selection: {args}")
                response = self.orchestrator.process_user_selection(args)
                print(f"\n{response}")
                
            elif cmd == 'status':
                status = self.orchestrator.get_current_status()
                print(f"\n📊 Current Status:")
                print(f"  Phase: {status['current_phase']}")
                print(f"  Selected Instruments: {status['selected_instruments']}")
                print(f"  Analysis Results: {status['analysis_results']}")
                print(f"  Timestamp: {status['timestamp']}")
                
            elif cmd == 'reset':
                self.orchestrator.reset_workflow()
                print("🔄 Workflow reset successfully")
                
            else:
                print(f"❌ Unknown command: {cmd}")
                print("Type 'help' for available commands")
                
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            print(f"❌ Error: {str(e)}")
        
        return True
    
    def run(self):
        """Run the interactive CLI."""
        self.print_banner()
        self.print_help()
        
        while self.running:
            try:
                # Get user input
                user_input = input("\n🤖 AI Agent > ").strip()
                
                # Process command
                self.running = self.process_command(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                print(f"❌ Unexpected error: {str(e)}")

def main():
    """Main entry point."""
    try:
        cli = InteractiveCLI()
        cli.run()
    except Exception as e:
        logger.error(f"Failed to start CLI: {str(e)}")
        print(f"❌ Failed to start CLI: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 