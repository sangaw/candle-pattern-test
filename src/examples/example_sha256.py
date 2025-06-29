#!/usr/bin/env python3
"""
Example script demonstrating SHA-256 hash generation for Kite Connect API.
"""
import sys
import os

# Import from parent directory (src)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from auth.token_generator import generate_sha256_hash, generate_sha256_hash_from_config

def main():
    """Demonstrate SHA-256 hash generation."""
    print("SHA-256 Hash Generation Example")
    print("=" * 40)
    
    # Example 1: Direct hash generation with provided values
    print("\n1. Direct hash generation:")
    api_key = "your_api_key_here"
    request_token = "your_request_token_here"
    api_secret = "your_api_secret_here"
    
    hash_result = generate_sha256_hash(api_key, request_token, api_secret)
    print(f"API Key: {api_key}")
    print(f"Request Token: {request_token}")
    print(f"API Secret: {api_secret}")
    print(f"SHA-256 Hash: {hash_result}")
    
    # Example 2: Hash generation from config file
    print("\n2. Hash generation from config file:")
    print("(This requires config/local-settings.json to exist)")
    
    try:
        # You would need to provide a request token here
        request_token_from_user = input("Enter request token (or press Enter to skip): ").strip()
        
        if request_token_from_user:
            hash_from_config = generate_sha256_hash_from_config(request_token_from_user)
            if hash_from_config:
                print(f"SHA-256 Hash from config: {hash_from_config}")
            else:
                print("Failed to generate hash from config")
        else:
            print("Skipped config-based hash generation")
    except Exception as e:
        print(f"Error with config-based generation: {e}")
    
    # Example 3: Show the concatenation process
    print("\n3. Concatenation process:")
    concatenated = api_key + request_token + api_secret
    print(f"Concatenated string: {concatenated}")
    print(f"String length: {len(concatenated)}")
    print(f"SHA-256 hash: {hash_result}")
    
    print("\n" + "=" * 40)
    print("Note: Replace the placeholder values with your actual API credentials")

if __name__ == "__main__":
    main() 