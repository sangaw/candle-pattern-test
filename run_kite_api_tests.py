"""
Standalone script to test all Kite Connect APIs.
Run from project root: python run_kite_api_tests.py
"""
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Change working directory to src/kite-apis for imports
os.chdir(os.path.join(src_path, 'kite-apis'))
# Ensure current working directory is on import path
sys.path.insert(0, os.getcwd())

# Now import and run
from test_all_apis import APITestRunner

if __name__ == "__main__":
    print("="*80)
    print("KITE CONNECT API TEST RUNNER")
    print("="*80)
    print()
    
    runner = APITestRunner()
    runner.run_all_tests()
    
    print()
    print("="*80)
    print("Check logs/kite_api_client.log for detailed request/response logs")
    print("="*80)

