#!/usr/bin/env python3
"""
Web-based Chatbot for AI Instrument Analysis
Provides a modern web interface for the instrument analysis workflow.
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, render_template, request, jsonify, session
from .orchestrator import InstrumentAnalysisOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'ai_instrument_analysis_secret_key'

# Global orchestrator instance
orchestrator = None

def get_orchestrator():
    """Get or create orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        orchestrator = InstrumentAnalysisOrchestrator()
    return orchestrator

@app.route('/')
def index():
    """Main chat interface."""
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Get orchestrator
        orch = get_orchestrator()
        
        # Check if this is a selection (numbers or names)
        is_selection = _is_selection_input(message)
        logger.info(f"Message: '{message}' | Is selection: {is_selection}")
        
        if is_selection:
            # Process selection
            response = orch.process_user_selection(message)
            message_type = 'selection_response'
        else:
            # Process new analysis request
            response = orch.start_analysis(message)
            message_type = 'analysis_response'
        
        # Get current status
        status = orch.get_current_status()
        
        # Format response for chat
        chat_response = {
            'message': response,
            'type': message_type,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        }
        
        return jsonify(chat_response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': f'Error processing message: {str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current workflow status."""
    try:
        orch = get_orchestrator()
        status = orch.get_current_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_workflow():
    """Reset the workflow."""
    try:
        orch = get_orchestrator()
        orch.reset_workflow()
        return jsonify({'message': 'Workflow reset successfully'})
    except Exception as e:
        logger.error(f"Error resetting workflow: {str(e)}")
        return jsonify({'error': str(e)}), 500

def _is_selection_input(message: str) -> bool:
    """Check if the message is a selection input."""
    # Check for number patterns (1,2,3 or 1 2 3)
    import re
    number_pattern = r'^\s*\d+(\s*[,\s]\s*\d+)*\s*$'
    if re.match(number_pattern, message):
        return True
    
    # Check for short instrument names only (not full sentences)
    message_lower = message.lower().strip()
    
    # If it's a short message (likely a selection)
    if len(message_lower.split()) <= 3:
        instrument_names = ['nifty', 'banknifty', 'reliance', 'tcs', 'infy', 'hdfc', 'icici']
        return any(name in message_lower for name in instrument_names)
    
    return False

def create_templates():
    """Create HTML templates directory and files."""
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Create the main HTML template
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Instrument Analysis Chatbot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 80vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message.bot {
            justify-content: flex-start;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.4;
        }
        
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .message.bot .message-content {
            background: white;
            color: #333;
            border: 1px solid #e1e5e9;
            border-bottom-left-radius: 4px;
        }
        
        .message-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            margin: 0 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
        }
        
        .message.user .message-avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .message.bot .message-avatar {
            background: #28a745;
            color: white;
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e1e5e9;
        }
        
        .chat-input-wrapper {
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e1e5e9;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .chat-input:focus {
            border-color: #667eea;
        }
        
        .send-button {
            padding: 12px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: transform 0.2s;
        }
        
        .send-button:hover {
            transform: translateY(-2px);
        }
        
        .send-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .quick-actions {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        
        .quick-action {
            padding: 8px 16px;
            background: #f8f9fa;
            border: 1px solid #e1e5e9;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s;
        }
        
        .quick-action:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .status-bar {
            padding: 10px 20px;
            background: #f8f9fa;
            border-top: 1px solid #e1e5e9;
            font-size: 12px;
            color: #666;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #28a745;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
        }
        
        .success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 10px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 AI Instrument Analysis</h1>
            <p>Ask me to analyze any instrument or find specific instruments</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-avatar">AI</div>
                <div class="message-content">
                    Hello! I'm your AI instrument analysis assistant. I can help you:
                    <br><br>
                    • Search for instruments by name or symbol<br>
                    • Filter by exchange (NSE, BSE, NFO)<br>
                    • Filter by type (Equity, Futures, Options)<br>
                    • Analyze candlestick patterns<br><br>
                    Try asking me something like:<br>
                    "I want to analyze NIFTY" or "Show me RELIANCE stock"
                </div>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <div>AI is thinking...</div>
        </div>
        
        <div class="status-bar">
            <div class="status-indicator">
                <div class="status-dot" id="statusDot"></div>
                <span id="statusText">Ready</span>
            </div>
            <div id="sessionInfo">Session: <span id="sessionId">default</span></div>
        </div>
        
        <div class="chat-input-container">
            <div class="chat-input-wrapper">
                <input type="text" id="chatInput" class="chat-input" placeholder="Type your message here..." autocomplete="off">
                <button id="sendButton" class="send-button">Send</button>
            </div>
            <div class="quick-actions">
                <div class="quick-action" onclick="sendQuickMessage('I want to analyze NIFTY')">Analyze NIFTY</div>
                <div class="quick-action" onclick="sendQuickMessage('Show me BANKNIFTY futures')">BANKNIFTY Futures</div>
                <div class="quick-action" onclick="sendQuickMessage('Find RELIANCE stock')">RELIANCE Stock</div>
                <div class="quick-action" onclick="sendQuickMessage('TCS analysis')">TCS Analysis</div>
                <div class="quick-action" onclick="resetWorkflow()">Reset</div>
            </div>
        </div>
    </div>

    <script>
        let sessionId = 'session_' + Date.now();
        let isProcessing = false;
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('sessionId').textContent = sessionId;
            document.getElementById('chatInput').focus();
            
            // Enter key to send
            document.getElementById('chatInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !isProcessing) {
                    sendMessage();
                }
            });
            
            // Send button click
            document.getElementById('sendButton').addEventListener('click', function() {
                if (!isProcessing) {
                    sendMessage();
                }
            });
        });
        
        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            
            if (!message || isProcessing) return;
            
            // Add user message
            addMessage(message, 'user');
            input.value = '';
            
            // Show loading
            setProcessing(true);
            
            // Send to API
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    session_id: sessionId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    addMessage('❌ Error: ' + data.error, 'bot');
                } else {
                    addMessage(data.message, 'bot');
                    updateStatus(data.status);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('❌ Network error. Please try again.', 'bot');
            })
            .finally(() => {
                setProcessing(false);
            });
        }
        
        function sendQuickMessage(message) {
            document.getElementById('chatInput').value = message;
            sendMessage();
        }
        
        function addMessage(content, sender) {
            const messagesContainer = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = sender === 'user' ? 'U' : 'AI';
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            messageContent.innerHTML = content.replace(/\\n/g, '<br>');
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            messagesContainer.appendChild(messageDiv);
            
            // Scroll to bottom
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        
        function setProcessing(processing) {
            isProcessing = processing;
            const loading = document.getElementById('loading');
            const sendButton = document.getElementById('sendButton');
            const chatInput = document.getElementById('chatInput');
            
            if (processing) {
                loading.classList.add('show');
                sendButton.disabled = true;
                chatInput.disabled = true;
            } else {
                loading.classList.remove('show');
                sendButton.disabled = false;
                chatInput.disabled = false;
                chatInput.focus();
            }
        }
        
        function updateStatus(status) {
            const statusText = document.getElementById('statusText');
            const statusDot = document.getElementById('statusDot');
            
            if (status) {
                statusText.textContent = `Phase: ${status.current_phase} | Instruments: ${status.selected_instruments}`;
                
                // Update status dot color
                if (status.current_phase === 'idle') {
                    statusDot.style.background = '#28a745';
                } else if (status.current_phase === 'discovery') {
                    statusDot.style.background = '#ffc107';
                } else if (status.current_phase === 'data_collection') {
                    statusDot.style.background = '#17a2b8';
                } else {
                    statusDot.style.background = '#6c757d';
                }
            }
        }
        
        function resetWorkflow() {
            if (isProcessing) return;
            
            setProcessing(true);
            
            fetch('/api/reset', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    addMessage('❌ Error: ' + data.error, 'bot');
                } else {
                    addMessage('🔄 Workflow reset successfully. You can start a new analysis.', 'bot');
                    updateStatus({current_phase: 'idle', selected_instruments: 0});
                }
            })
            .catch(error => {
                console.error('Error:', error);
                addMessage('❌ Error resetting workflow.', 'bot');
            })
            .finally(() => {
                setProcessing(false);
            });
        }
    </script>
</body>
</html>'''
    
    with open(os.path.join(templates_dir, 'chatbot.html'), 'w') as f:
        f.write(html_template)

def main():
    """Main entry point."""
    try:
        # Create templates
        create_templates()
        
        # Start the web server
        print("🤖 Starting AI Instrument Analysis Chatbot...")
        print("🌐 Access the chatbot at: http://127.0.0.1:5001")
        print("📱 Modern web interface with quick actions")
        print("🔄 Press Ctrl+C to stop the server")
        
        app.run(host='127.0.0.1', port=5001, debug=False)
        
    except Exception as e:
        logger.error(f"Failed to start chatbot: {str(e)}")
        print(f"❌ Failed to start chatbot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 