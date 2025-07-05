#!/usr/bin/env python3
"""
Launcher for Tool-Based Agent Web Chatbot
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.ai_agent.tool_based_agent.tool_based_web_chatbot_enhanced import app

if __name__ == "__main__":
    print("🤖 Starting Enhanced Tool-Based AI Instrument Analysis Chatbot...")
    print("🌐 Access the chatbot at: http://127.0.0.1:5003")
    print("📝 Detailed logs saved to: logs/web_chatbot_*.log")
    print("📱 Enhanced web interface with comprehensive logging")
    print("🔄 Press Ctrl+C to stop the server")
    
    app.run(host='127.0.0.1', port=5003, debug=False) 