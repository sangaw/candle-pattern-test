#!/usr/bin/env python3
"""
Helper script to get Kite Connect request token.
"""
import json
import webbrowser
from urllib.parse import urlencode

def load_kite_config():
    """Load Kite Connect configuration."""
    config_path = 'config/local-settings.json'
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get('kite_connect', {})
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def generate_login_url():
    """Generate the Kite Connect login URL."""
    kite_config = load_kite_config()
    api_key = kite_config.get('api_key')
    
    if not api_key:
        print("❌ API key not found in config/local-settings.json")
        return None
    
    # Kite Connect login URL
    base_url = "https://kite.zerodha.com/connect/login"
    params = {
        'api_key': api_key,
        'v': '3'
    }
    
    login_url = f"{base_url}?{urlencode(params)}"
    return login_url

def main():
    """Main function to help get request token."""
    print("🔑 Kite Connect Request Token Helper")
    print("=" * 50)
    
    # Load config
    kite_config = load_kite_config()
    api_key = kite_config.get('api_key')
    
    if not api_key:
        print("❌ API key not found in config/local-settings.json")
        print("Please ensure your config file has the correct API key.")
        return
    
    print(f"✅ API Key found: {api_key}")
    print()
    
    # Generate login URL
    login_url = generate_login_url()
    if not login_url:
        return
    
    print("📋 Steps to get Request Token:")
    print("1. Click the login URL below (or copy and paste in browser)")
    print("2. Login with your Zerodha credentials")
    print("3. Complete 2FA if required")
    print("4. You'll be redirected to a URL containing the request token")
    print("5. Copy the request token from the URL")
    print()
    
    print("🔗 Login URL:")
    print(login_url)
    print()
    
    # Ask if user wants to open browser
    open_browser = input("Would you like to open this URL in your browser? (y/n): ").strip().lower()
    if open_browser in ['y', 'yes']:
        try:
            webbrowser.open(login_url)
            print("✅ Browser opened with login URL")
        except Exception as e:
            print(f"❌ Could not open browser: {e}")
            print("Please copy and paste the URL manually")
    
    print()
    print("📝 After getting the request token, run:")
    print("   python src/auth/token_generator.py")
    print()
    print("💡 The request token will be in the redirect URL after login")
    print("   Example: https://your-app.com/?action=login&status=success&request_token=YOUR_TOKEN")

if __name__ == "__main__":
    main() 