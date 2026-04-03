"""
Minimal BA Agent - Works without Docker
Uses mock data for database connections
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import uuid
from loguru import logger

# Initialize FastAPI
app = FastAPI(title="BA Agent", description="Business Analyst Autonomous Agent")

# Request/Response models
class UserRequest(BaseModel):
    input: str
    user_id: str
    channel: str = "api"

class AgentResponse(BaseModel):
    session_id: str
    status: str
    output: str
    needs_approval: bool = False

# In-memory storage (replace with database later)
sessions = {}

@app.get("/")
async def root():
    return {
        "agent": "BA Agent",
        "status": "running",
        "version": "1.0.0",
        "note": "Running without Docker - Neo4j, PostgreSQL, and Ollama not available"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: UserRequest):
    """Process user input and generate BA response"""
    session_id = str(uuid.uuid4())
    
    logger.info(f"Processing request from {request.user_id}: {request.input[:50]}...")
    
    # Simple response logic (mock BA behavior)
    if "requirement" in request.input.lower() or "need" in request.input.lower():
        output = f"""📋 **Requirements Analysis**

Based on your input: "{request.input}"

**User Story:**
As a stakeholder, I want {request.input.lower()} so that business value is delivered.

**Acceptance Criteria:**
1. Feature works as described
2. Edge cases handled
3. Documentation updated

**Next Steps:**
- Review this requirement with the team
- Estimate effort (2-5 story points)
- Add to backlog
"""
    elif "bug" in request.input.lower() or "issue" in request.input.lower():
        output = f"""🐛 **Bug Analysis**

Issue: {request.input}

**Impact Assessment:**
- Severity: Medium
- Affected Users: All
- Workaround: None identified

**Recommended Action:**
1. Reproduce the issue
2. Root cause analysis
3. Fix and deploy
"""
    elif "report" in request.input.lower() or "analyz" in request.input.lower():
        output = f"""📊 **Analysis Report**

Request: {request.input}

**Findings:**
- Data indicates normal operations
- No anomalies detected
- System performance within parameters

**Recommendations:**
- Continue monitoring
- Schedule monthly review
"""
    else:
        output = f"""💡 **BA Assistant Response**

I understand you're asking about: "{request.input}"

As a Business Analyst, I can help you with:
- Writing user stories and acceptance criteria
- Analyzing gaps in business processes
- Creating requirements documents
- Impact analysis for changes

Please provide more specific details about your need.
"""
    
    # Store session
    sessions[session_id] = {
        "input": request.input,
        "user_id": request.user_id,
        "timestamp": datetime.now().isoformat(),
        "output": output
    }
    
    return AgentResponse(
        session_id=session_id,
        status="completed",
        output=output,
        needs_approval=False
    )

@app.get("/agent/status/{session_id}")
async def get_status(session_id: str):
    """Get session status"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "status": "completed",
        "data": sessions[session_id]
    }

@app.get("/agent/sessions")
async def list_sessions():
    """List all sessions"""
    return {"sessions": list(sessions.keys()), "count": len(sessions)}

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("BA Agent Starting...")
    print("=" * 50)
    print("API available at: http://localhost:8000")
    print("Documentation: http://localhost:8000/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
