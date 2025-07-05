#!/usr/bin/env python3
"""
Enhanced Tool-Based Web Chatbot with Detailed Logging
A web interface for the tool-based AI agent with comprehensive logging.
"""
import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from .tool_based_agent import ToolBasedAgent

# Configure comprehensive logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Create a detailed log file for web interactions
log_file = os.path.join(log_dir, f'web_chatbot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the tool-based agent
agent = ToolBasedAgent()

def log_web_interaction(user_input: str, response: dict, session_id: str = None):
    """Log web interactions with detailed information."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'session_id': session_id or 'default',
        'user_input': user_input,
        'agent_response': response,
        'agent_status': agent.get_status()
    }
    
    logger.info(f"=== WEB INTERACTION ===")
    logger.info(f"User Input: {user_input}")
    logger.info(f"Agent Response: {json.dumps(response, indent=2, default=str)}")
    logger.info(f"Agent Status: {json.dumps(agent.get_status(), indent=2, default=str)}")
    logger.info("=" * 50)

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 Enhanced AI Instrument Analysis Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            width: 90%;
            max-width: 900px;
            height: 85vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .status-indicator {
            position: absolute;
            top: 20px;
            right: 20px;
            width: 12px;
            height: 12px;
            background: #4CAF50;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
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
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        
        .message.bot .message-content pre {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        
        .quick-actions {
            padding: 15px 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .quick-action-btn {
            background: #f0f0f0;
            border: none;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s ease;
            color: #333;
        }
        
        .quick-action-btn:hover {
            background: #667eea;
            color: white;
            transform: translateY(-2px);
        }
        
        .chat-input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .chat-input-form {
            display: flex;
            gap: 10px;
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .chat-input:focus {
            border-color: #667eea;
        }
        
        .send-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .send-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .typing-indicator {
            display: none;
            padding: 12px 16px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            color: #666;
            font-style: italic;
        }
        
        .phase-indicator {
            background: #e3f2fd;
            color: #1976d2;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 10px;
            display: inline-block;
        }
        
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 12px 16px;
            border-radius: 8px;
            border-left: 4px solid #c62828;
            margin: 10px 0;
        }
        
        .success-message {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 12px 16px;
            border-radius: 8px;
            border-left: 4px solid #2e7d32;
            margin: 10px 0;
        }
        
        .tool-info {
            background: #f3e5f5;
            color: #7b1fa2;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 11px;
            margin-top: 5px;
            display: inline-block;
        }
        
        .debug-info {
            background: #fff3e0;
            color: #e65100;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 11px;
            margin-top: 5px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="status-indicator"></div>
            <h1>🤖 Enhanced AI Instrument Analysis Agent</h1>
            <p>Tool-Based Architecture with Detailed Logging</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-content">
                    <div class="phase-indicator">Phase: {{ agent_status.current_phase }}</div>
                    <p>Hello! I'm your enhanced AI instrument analysis assistant with detailed logging.</p>
                    <ul style="margin-left: 20px; margin-top: 10px;">
                        <li>🔍 Search for financial instruments</li>
                        <li>📊 Collect historical data</li>
                        <li>📈 Analyze candlestick patterns</li>
                        <li>🛠️ Use specialized tools for each task</li>
                        <li>📝 Detailed logging for debugging</li>
                    </ul>
                    <p style="margin-top: 15px;"><strong>Try asking:</strong> "Show me NIFTY futures" or "Find BANKNIFTY options"</p>
                    <div class="tool-info">Available Tools: {{ ', '.join(agent_status.available_tools) }}</div>
                    <div class="debug-info">Log File: {{ log_file }}</div>
                </div>
            </div>
        </div>
        
        <div class="quick-actions">
            <button class="quick-action-btn" onclick="sendQuickAction('Show me NIFTY futures')">NIFTY Futures</button>
            <button class="quick-action-btn" onclick="sendQuickAction('Find BANKNIFTY options')">BANKNIFTY Options</button>
            <button class="quick-action-btn" onclick="sendQuickAction('Search for Reliance stock')">Reliance Stock</button>
            <button class="quick-action-btn" onclick="sendQuickAction('Fetch data for selected instruments')">Fetch Data</button>
            <button class="quick-action-btn" onclick="sendQuickAction('Reset workflow')">Reset</button>
        </div>
        
        <div class="chat-input-container">
            <form class="chat-input-form" id="chatForm">
                <input type="text" class="chat-input" id="messageInput" 
                       placeholder="Ask me to search for instruments, fetch data, or analyze patterns..." 
                       autocomplete="off">
                <button type="submit" class="send-btn" id="sendBtn">Send</button>
            </form>
        </div>
    </div>
    
    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const chatForm = document.getElementById('chatForm');
        
        function addMessage(content, isUser = false) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            if (typeof content === 'string') {
                contentDiv.innerHTML = content.replace(/\\n/g, '<br>');
            } else {
                contentDiv.innerHTML = content;
            }
            
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function showTypingIndicator() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot';
            typingDiv.id = 'typingIndicator';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'typing-indicator';
            contentDiv.textContent = 'AI Agent is thinking...';
            
            typingDiv.appendChild(contentDiv);
            chatMessages.appendChild(typingDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function hideTypingIndicator() {
            const typingIndicator = document.getElementById('typingIndicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }
        
        function sendQuickAction(action) {
            messageInput.value = action;
            sendMessage();
        }
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            // Add user message
            addMessage(message, true);
            messageInput.value = '';
            sendBtn.disabled = true;
            
            // Show typing indicator
            showTypingIndicator();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                hideTypingIndicator();
                
                if (data.success) {
                    addMessage(data.response);
                    
                    // Update phase indicator if provided
                    if (data.phase) {
                        const phaseIndicator = document.querySelector('.phase-indicator');
                        if (phaseIndicator) {
                            phaseIndicator.textContent = `Phase: ${data.phase}`;
                        }
                    }
                } else {
                    addMessage(`<div class="error-message">❌ ${data.response}</div>`);
                }
                
            } catch (error) {
                hideTypingIndicator();
                addMessage(`<div class="error-message">❌ Error: ${error.message}</div>`);
            }
            
            sendBtn.disabled = false;
            messageInput.focus();
        }
        
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            sendMessage();
        });
        
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // Auto-focus input
        messageInput.focus();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the main chat interface."""
    agent_status = agent.get_status()
    return render_template_string(HTML_TEMPLATE, 
                                agent_status=agent_status,
                                log_file=log_file)

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with detailed logging."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                'success': False,
                'response': 'Please provide a message.'
            })
        
        logger.info(f"Received web message: {message}")
        
        # Process message with the tool-based agent
        result = agent.process_user_input(message)
        
        # Log the interaction
        log_web_interaction(message, result)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error processing web chat message: {str(e)}")
        error_response = {
            'success': False,
            'response': f'Error processing message: {str(e)}'
        }
        log_web_interaction(message if 'message' in locals() else 'unknown', error_response)
        return jsonify(error_response)

@app.route('/api/status')
def status():
    """Get agent status."""
    return jsonify(agent.get_status())

@app.route('/api/logs')
def get_logs():
    """Get recent logs for debugging."""
    try:
        with open(log_file, 'r') as f:
            logs = f.read()
        return jsonify({
            'success': True,
            'logs': logs[-5000:]  # Last 5000 characters
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🤖 Starting Enhanced Tool-Based AI Instrument Analysis Chatbot...")
    print(f"🌐 Access the chatbot at: http://127.0.0.1:5003")
    print(f"📝 Detailed logs saved to: {log_file}")
    print("📱 Enhanced web interface with comprehensive logging")
    print("🔄 Press Ctrl+C to stop the server")
    
    app.run(host='127.0.0.1', port=5003, debug=False) 