"""
BA Agent - Simple Working UI
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI()

# Store sessions
sessions = {}

class UserRequest(BaseModel):
    input: str
    user_id: str

class AgentResponse(BaseModel):
    session_id: str
    output: str
    intent: str

def analyze_request(user_input: str) -> tuple:
    input_lower = user_input.lower()
    
    if any(word in input_lower for word in ["need", "requirement", "feature", "want"]):
        intent = "requirements"
        output = f"""
📋 REQUIREMENTS ANALYSIS

User Story: As a stakeholder, I want {user_input} so that business value is delivered.

Acceptance Criteria:
1. Feature works as described
2. Edge cases are handled properly
3. Documentation is updated
4. Unit tests are written and passing

Estimated effort: 3-5 story points
"""
    elif any(word in input_lower for word in ["gap", "missing", "lack"]):
        intent = "gap_analysis"
        output = f"""
🔍 GAP ANALYSIS REPORT

Current State: {user_input} is not fully addressed

Identified Gaps:
1. Missing functionality
2. Documentation needs updating
3. Stakeholder alignment required

Recommendations: Schedule workshop, create implementation plan
"""
    else:
        intent = "general"
        output = f"""
💡 BA RESPONSE

I understand you're asking about: "{user_input}"

I can help you with requirements, gap analysis, documentation, and testing.
Please provide more specific details.
"""
    
    return intent, output

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: UserRequest):
    session_id = str(uuid.uuid4())
    intent, output = analyze_request(request.input)
    
    sessions[session_id] = {
        "user_id": request.user_id,
        "input": request.input,
        "intent": intent
    }
    
    return AgentResponse(session_id=session_id, output=output, intent=intent)

@app.get("/ui", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>BA Agent</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .chat-box {
            background: white;
            border-radius: 15px;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .user-msg {
            text-align: right;
            margin-bottom: 15px;
        }
        .user-msg span {
            background: #667eea;
            color: white;
            padding: 10px 15px;
            border-radius: 15px;
            display: inline-block;
            max-width: 70%;
        }
        .agent-msg {
            text-align: left;
            margin-bottom: 15px;
        }
        .agent-msg span {
            background: white;
            color: #333;
            padding: 10px 15px;
            border-radius: 15px;
            display: inline-block;
            max-width: 70%;
            border: 1px solid #ddd;
        }
        .input-area {
            display: flex;
            padding: 15px;
            background: white;
            border-top: 1px solid #ddd;
        }
        input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            margin-left: 10px;
            cursor: pointer;
        }
        .examples {
            padding: 10px;
            background: #f9f9f9;
            text-align: center;
        }
        .example-btn {
            background: #e0e0e0;
            padding: 5px 10px;
            margin: 3px;
            border-radius: 15px;
            font-size: 12px;
        }
        .status {
            text-align: center;
            padding: 5px;
            font-size: 12px;
            background: #e8f5e9;
        }
    </style>
</head>
<body>
    <div class="chat-box">
        <div class="header">
            <h2>🤖 BA Agent</h2>
            <p>Business Analyst AI Assistant</p>
        </div>
        
        <div class="messages" id="messages">
            <div class="agent-msg">
                <span>👋 Hello! Ask me about requirements, gaps, or documentation.</span>
            </div>
        </div>
        
        <div class="examples">
            <button class="example-btn" onclick="sendMsg('I need a login feature')">Login Feature</button>
            <button class="example-btn" onclick="sendMsg('We are missing inventory tracking')">Gap Analysis</button>
            <button class="example-btn" onclick="sendMsg('Document the API')">Documentation</button>
        </div>
        
        <div class="status" id="status">✅ Connected</div>
        
        <div class="input-area">
            <input type="text" id="msgInput" placeholder="Type your request...">
            <button onclick="sendMsg()">Send</button>
        </div>
    </div>

    <script>
        function addMessage(text, isUser) {
            const messagesDiv = document.getElementById('messages');
            const msgDiv = document.createElement('div');
            msgDiv.className = isUser ? 'user-msg' : 'agent-msg';
            msgDiv.innerHTML = '<span>' + text.replace(/\\n/g, '<br>') + '</span>';
            messagesDiv.appendChild(msgDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function sendMsg(exampleText) {
            let message;
            if (exampleText) {
                message = exampleText;
                document.getElementById('msgInput').value = '';
            } else {
                const input = document.getElementById('msgInput');
                message = input.value.trim();
                if (!message) return;
                input.value = '';
            }
            
            addMessage(message, true);
            
            fetch('/agent/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input: message, user_id: 'web_user' })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.output, false);
                document.getElementById('status').innerHTML = '✅ Connected';
            })
            .catch(error => {
                addMessage('❌ Error: Cannot connect to agent', false);
                document.getElementById('status').innerHTML = '🔴 Disconnected';
            });
        }
        
        document.getElementById('msgInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMsg();
            }
        });
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("BA AGENT STARTING...")
    print("UI: http://localhost:8000/ui")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
