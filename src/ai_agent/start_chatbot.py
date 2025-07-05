#!/usr/bin/env python3
"""
Launcher script for the AI Instrument Analysis Chatbot
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from ai_agent.web_chatbot import main
    main() 