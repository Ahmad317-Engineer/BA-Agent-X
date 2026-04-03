"""
BA Agent API - With State Machine
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.state import AgentContext
from src.agent.workflow import create_agent_graph

# Initialize FastAPI
app = FastAPI(
    title="BA Agent - Business Analyst Autonomous Agent",
    description="AI agent that acts as a real Business Analyst",
    version="2.0.0"
)

# Initialize agent graph
agent_graph = create_agent_graph()

# Store sessions
sessions: Dict[str, Dict[str, Any]] = {}

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
    error: Optional[str] = None

@app.get("/")
async def root():
    return {
        "agent": "BA Agent v2",
        "status": "running",
        "description": "Business Analyst Autonomous Agent with State Machine",
        "endpoints": [
            "POST /agent/run - Process user input",
            "GET /agent/status/{session_id} - Get session status",
            "GET /agent/sessions - List all sessions",
            "GET /health - Health check"
        ]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0"
    }

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: UserRequest):
    """Process user input through the agent state machine"""
    
    session_id = str(uuid.uuid4())
    
    # Create initial context
    context = AgentContext(
        session_id=session_id,
        user_id=request.user_id,
        channel=request.channel,
        original_input=request.input
    )
    
    try:
        # Run the agent workflow
        result = agent_graph.invoke(context)
        
        # Store session
        sessions[session_id] = {
            "user_id": request.user_id,
            "input": request.input,
            "intent": result.intent.value if result.intent else "unknown",
            "output": result.draft_content,
            "status": result.state.value,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat()
        }
        
        return AgentResponse(
            session_id=session_id,
            status=result.state.value,
            intent=result.intent.value if result.intent else "unknown",
            output=result.draft_content or "Processing complete",
            needs_approval=result.requires_human_approval,
            error=result.error
        )
    
    except Exception as e:
        sessions[session_id] = {
            "user_id": request.user_id,
            "input": request.input,
            "error": str(e),
            "status": "error"
        }
        
        return AgentResponse(
            session_id=session_id,
            status="error",
            intent="unknown",
            output="An error occurred processing your request",
            needs_approval=False,
            error=str(e)
        )

@app.get("/agent/status/{session_id}")
async def get_status(session_id: str):
    """Get session status and results"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return sessions[session_id]

@app.get("/agent/sessions")
async def list_sessions(limit: int = 10):
    """List recent sessions"""
    recent_sessions = list(sessions.keys())[-limit:]
    return {
        "total": len(sessions),
        "sessions": recent_sessions,
        "limit": limit
    }

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("BA AGENT v2 - WITH STATE MACHINE")
    print("=" * 60)
    print("?? Starting server...")
    print("?? API: http://localhost:8000")
    print("?? Docs: http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, )
