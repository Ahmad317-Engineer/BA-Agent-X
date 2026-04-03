"""
Production BA Agent API - Complete implementation
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import time

from src.utils.logging import setup_logging, metrics
from src.tools.slack_bot import SlackBot

# Setup logging
logger = setup_logging()

# Initialize FastAPI
app = FastAPI(
    title="BA Agent - Business Analyst Autonomous Agent",
    description="Production-ready Business Analyst AI Agent",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Slack bot
slack_bot = SlackBot()

# Store sessions
sessions: Dict[str, Dict] = {}

class UserRequest(BaseModel):
    input: str
    user_id: str
    channel: str = "api"

class AgentResponse(BaseModel):
    session_id: str
    status: str
    intent: str
    output: str
    needs_approval: bool = False
    processing_time_ms: float = 0
    error: Optional[str] = None

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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all requests"""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration_ms:.2f}ms")
    return response

@app.get("/")
async def root():
    return {
        "agent": "BA Agent",
        "status": "running",
        "version": "3.0.0",
        "endpoints": [
            "POST /agent/run - Process user input",
            "GET /agent/status/{session_id} - Get session status",
            "GET /agent/sessions - List all sessions",
            "GET /metrics - Get agent metrics",
            "GET /health - Health check"
        ]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/metrics")
async def get_metrics():
    """Get agent metrics"""
    return metrics.get_metrics()

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: UserRequest):
    """Process user input through the agent"""
    start_time = time.time()
    session_id = str(uuid.uuid4())
    
    logger.info(f"Processing request from {request.user_id}: {request.input[:50]}...")
    
    try:
        intent, output = analyze_request(request.input)
        
        # Record metrics
        metrics.record_request(intent, 0)
        
        # Store session
        sessions[session_id] = {
            "user_id": request.user_id,
            "input": request.input,
            "intent": intent,
            "output": output,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to Slack if channel is slack
        if request.channel == "slack":
            slack_response = slack_bot.format_agent_response({
                'intent': intent,
                'session_id': session_id,
                'output': output,
                'needs_approval': False
            })
            slack_bot.send_message("#ba-agent", output[:500], slack_response)
        
        processing_time = (time.time() - start_time) * 1000
        
        return AgentResponse(
            session_id=session_id,
            status="completed",
            intent=intent,
            output=output,
            needs_approval=False,
            processing_time_ms=processing_time
        )
    
    except Exception as e:
        metrics.record_error()
        logger.error(f"Error processing request: {e}", extra={'extra_data': {'user_id': request.user_id}})
        
        return AgentResponse(
            session_id=session_id,
            status="error",
            intent="unknown",
            output="An error occurred processing your request",
            needs_approval=False,
            processing_time_ms=(time.time() - start_time) * 1000,
            error=str(e)
        )

@app.get("/agent/status/{session_id}")
async def get_status(session_id: str):
    """Get session status"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@app.get("/agent/sessions")
async def list_sessions(limit: int = 10):
    """List recent sessions"""
    recent = list(sessions.keys())[-limit:]
    return {
        "total": len(sessions),
        "sessions": recent,
        "limit": limit
    }

@app.post("/agent/approve/{session_id}")
async def approve_session(session_id: str, approved: bool = True):
    """Approve or reject a session (for human-in-loop)"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sessions[session_id]["approved"] = approved
    sessions[session_id]["approved_at"] = datetime.now().isoformat()
    
    return {"session_id": session_id, "approved": approved}

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🚀 BA AGENT - PRODUCTION VERSION")
    print("=" * 60)
    print("📡 API: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("📊 Metrics: http://localhost:8000/metrics")
    print("=" * 60)
    print("\n✅ Agent is ready! Press Ctrl+C to stop.\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
