#!/usr/bin/env python3
"""
Launcher for Base Agent Web Chatbot
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ai_agent.base_agent.web_chatbot import app

if __name__ == "__main__":
    print("🤖 Starting Base Agent Web Chatbot...")
    print("🌐 Access the chatbot at: http://127.0.0.1:5001")
    print("📱 Web interface for instrument analysis")
    print("🔄 Press Ctrl+C to stop the server")
    
    app.run(host='127.0.0.1', port=5001, debug=False) 