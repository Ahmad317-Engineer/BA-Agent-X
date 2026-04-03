"""
BA Agent with Built-in UI - FIXED VERSION
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="BA Agent", description="Business Analyst Assistant")

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
    """Simple intent analysis"""
    input_lower = user_input.lower()
    
    if any(word in input_lower for word in ["need", "requirement", "feature", "want"]):
        intent = "requirements"
        output = f"""
📋 **REQUIREMENTS ANALYSIS**

**User Story:**
As a stakeholder, I want {user_input} so that business value is delivered.

**Acceptance Criteria:**
1. Feature works as described
2. Edge cases are handled properly
3. Documentation is updated
4. Unit tests are written and passing

**Technical Considerations:**
- Estimated effort: 3-5 story points
- Dependencies: None identified
- Risks: Low to medium

**Next Steps:**
- Review with team
- Break down into tasks
- Add to sprint backlog
"""
    elif any(word in input_lower for word in ["gap", "missing", "lack"]):
        intent = "gap_analysis"
        output = f"""
🔍 **GAP ANALYSIS REPORT**

**Current State:** {user_input} is not fully addressed

**Desired State:** Complete solution with all requirements met

**Identified Gaps:**
1. Missing functionality in current system
2. Documentation needs updating
3. Stakeholder alignment required

**Recommendations:**
1. Schedule requirements workshop
2. Create implementation plan
3. Assign ownership and timeline
"""
    elif any(word in input_lower for word in ["document", "write", "create"]):
        intent = "documentation"
        output = f"""
📄 **DOCUMENTATION REQUEST**

**Topic:** {user_input}

**Documentation Structure:**
1. **Overview** - What this covers
2. **Prerequisites** - What users need
3. **Step-by-Step Guide** - How to use
4. **Troubleshooting** - Common issues
5. **FAQ** - Frequently asked questions
"""
    elif any(word in input_lower for word in ["test", "scenario"]):
        intent = "testing"
        output = f"""
🧪 **TEST PLAN**

**Test Scenario:** {user_input}

**Test Cases:**
1. **Happy Path** - Normal operation works
2. **Edge Cases** - Boundary conditions
3. **Error Handling** - Invalid inputs
4. **Performance** - Load testing
"""
    else:
        intent = "general"
        output = f"""
💡 **BA ASSISTANT RESPONSE**

I understand you're asking about: "{user_input}"

As a Business Analyst, I can help you with:
- **Requirements Gathering** - "I need a login feature"
- **Gap Analysis** - "We're missing inventory tracking"
- **Documentation** - "Please document the API"
- **Testing** - "Test the checkout process"

Please provide more specific details about your business need.
"""
    
    return intent, output

@app.get("/")
async def root():
    return {"agent": "BA Agent", "status": "running", "version": "1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: UserRequest):
    session_id = str(uuid.uuid4())
    intent, output = analyze_request(request.input)
    
    sessions[session_id] = {
        "user_id": request.user_id,
        "input": request.input,
        "intent": intent,
        "timestamp": datetime.now().isoformat()
    }
    
    return AgentResponse(session_id=session_id, output=output, intent=intent)

@app.get("/agent/status/{session_id}")
async def get_status(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@app.get("/agent/sessions")
async def list_sessions():
    return {"total": len(sessions), "sessions": list(sessions.keys())}

# Serve the UI
@app.get("/ui", response_class=HTMLResponse)
async def serve_ui():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>BA Agent - Business Analyst AI</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 32px; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .chat-area {
            height: 450px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 20px;
            display: flex;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user { justify-content: flex-end; }
        .message.agent { justify-content: flex-start; }
        .bubble {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        .user .bubble {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .agent .bubble {
            background: white;
            border: 1px solid #e0e0e0;
            color: #333;
        }
        .examples {
            padding: 15px 20px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
        }
        .example-btn {
            background: #e9ecef;
            border: none;
            padding: 8px 16px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }
        .example-btn:hover { background: #667eea; color: white; }
        .input-area {
            padding: 20px;
            display: flex;
            gap: 10px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }
        .input-area input:focus { border-color: #667eea; }
        .input-area button {
            padding: 12px 28px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
        }
        .typing {
            padding: 10px 20px;
            color: #999;
            font-size: 12px;
            display: none;
            background: #f8f9fa;
        }
        .typing.active { display: block; }
        .status {
            text-align: center;
            padding: 10px;
            font-size: 12px;
            background: #e8f5e9;
            color: #2e7d32;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 BA Agent</h1>
            <p>Your Autonomous Business Analyst Assistant</p>
        </div>
        
        <div class="chat-area" id="chatArea">
            <div class="message agent">
                <div class="bubble">
                    👋 Hello! I'm your BA Agent.<br><br>
                    I can help you with:<br>
                    • 📋 Requirements & User Stories<br>
                    • 🔍 Gap Analysis<br>
                    • 📚 Documentation<br>
                    • 🧪 Test Scenarios<br><br>
                    <strong>Try asking:</strong> "I need a login feature for my app"
                </div>
            </div>
        </div>
        
        <div class="examples">
            <strong>📝 Quick Examples:</strong>
            <button class="example-btn" onclick="sendExample('I need a user authentication system with MFA')">🔐 Authentication</button>
            <button class="example-btn" onclick="sendExample('We are missing inventory tracking')">📦 Gap Analysis</button>
            <button class="example-btn" onclick="sendExample('Please document the API authentication flow')">📚 Documentation</button>
            <button class="example-btn" onclick="sendExample('Test the login feature with invalid passwords')">🧪 Testing</button>
        </div>
        
        <div class="typing" id="typing">🤖 BA Agent is analyzing your request...</div>
        <div class="status" id="status">✅ Connected to BA Agent</div>
        
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Describe your business analysis request..." onkeypress="if(event.key===Enter) sendMessage()">
            <button onclick="sendMessage()">Send →</button>
        </div>
    </div>

    <script>
        function addMessage(content, isUser) {
            const chatArea = document.getElementById('chatArea');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (isUser ? 'user' : 'agent');
            let formattedContent = content.replace(/\n/g, '<br>');
            messageDiv.innerHTML = '<div class="bubble">' + formattedContent + '</div>';
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }
        
        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;
            
            addMessage(message, true);
            input.value = '';
            
            const typing = document.getElementById('typing');
            typing.classList.add('active');
            
            try {
                const response = await fetch('/agent/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ input: message, user_id: 'web_user' })
                });
                
                const data = await response.json();
                addMessage(data.output, false);
                document.getElementById('status').innerHTML = '✅ Connected to BA Agent';
                
            } catch (error) {
                addMessage('❌ Error: Cannot connect to BA Agent.', false);
                document.getElementById('status').innerHTML = '🔴 Disconnected from BA Agent';
            } finally {
                typing.classList.remove('active');
            }
        }
        
        function sendExample(text) {
            document.getElementById('userInput').value = text;
            sendMessage();
        }
        
        async function checkConnection() {
            try {
                const response = await fetch('/health');
                if (response.ok) {
                    document.getElementById('status').innerHTML = '✅ Connected to BA Agent';
                }
            } catch (error) {
                document.getElementById('status').innerHTML = '🔴 Disconnected from BA Agent';
            }
        }
        
        checkConnection();
        setInterval(checkConnection, 30000);
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 BA AGENT WITH UI (FIXED)")
    print("=" * 60)
    print("📡 API: http://localhost:8000")
    print("🎨 UI: http://localhost:8000/ui")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    print("\n✅ Agent is ready! Press Ctrl+C to stop.\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
