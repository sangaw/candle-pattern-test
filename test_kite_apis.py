"""
Test all Kite Connect APIs and log results.
Run from project root: python test_kite_apis.py
"""
import sys
import os
sys.path.insert(0, 'src')

# Change to kite-apis directory for imports
original_cwd = os.getcwd()
os.chdir('src/kite-apis')

try:
    from test_all_apis import APITestRunner
    
    print("="*80)
    print("KITE CONNECT API TEST RUNNER")
    print("="*80)
    print()
    
    runner = APITestRunner()
    runner.run_all_tests()
    
    print()
    print("="*80)
    print("Test completed! Check the following logs:")
    print("  - logs/kite_api_client.log (detailed request/response logs)")
    print("  - logs/api_test_results_*.json (summary results)")
    print("="*80)
    
except Exception as e:
    print(f"Error running tests: {e}")
    import traceback
    traceback.print_exc()
finally:
    os.chdir(original_cwd)

