"""
BA Agent - Production Backend for Render
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid
import os

app = FastAPI()

# Add CORS for frontend (important for Vercel)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will restrict to your Vercel URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
📋 **REQUIREMENTS ANALYSIS**

**User Story:**
As a stakeholder, I want {user_input} so that business value is delivered.

**Acceptance Criteria:**
1. Feature works as described
2. Edge cases are handled properly
3. Documentation is updated
4. Unit tests are written and passing

**Estimated effort:** 3-5 story points
"""
    elif any(word in input_lower for word in ["gap", "missing", "lack"]):
        intent = "gap_analysis"
        output = f"""
🔍 **GAP ANALYSIS REPORT**

**Current State:** {user_input} is not fully addressed

**Identified Gaps:**
1. Missing functionality in current system
2. Documentation needs updating
3. Stakeholder alignment required

**Recommendations:**
Schedule requirements workshop and create implementation plan
"""
    elif any(word in input_lower for word in ["document", "write", "create"]):
        intent = "documentation"
        output = f"""
📄 **DOCUMENTATION REQUEST**

**Topic:** {user_input}

**Documentation Structure:**
1. Overview
2. Prerequisites
3. Step-by-Step Guide
4. Troubleshooting
5. FAQ
"""
    elif any(word in input_lower for word in ["test", "scenario"]):
        intent = "testing"
        output = f"""
🧪 **TEST PLAN**

**Test Scenario:** {user_input}

**Test Cases:**
1. Happy Path
2. Edge Cases
3. Error Handling
4. Performance
"""
    else:
        intent = "general"
        output = f"""
💡 **BA ASSISTANT RESPONSE**

I understand you're asking about: "{user_input}"

I can help you with:
- Requirements Gathering
- Gap Analysis
- Documentation
- Testing

Please provide more specific details.
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
