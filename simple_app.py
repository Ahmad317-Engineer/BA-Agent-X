"""
Simple BA Agent - Standalone Version
No complex imports needed - just works!
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
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

**Priority:** High - impacts business operations
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

**Estimated Pages:** 3-5
**Target Audience:** End users and administrators
**Format:** Markdown or Confluence
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

**Acceptance Criteria:**
- All test cases pass
- No regression issues
- Performance meets SLAs

**Estimated Test Effort:** 2-4 hours
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

Please provide more specific details about your business need, and I'll provide a detailed analysis.
"""
    
    return intent, output

@app.get("/")
async def root():
    return {
        "agent": "BA Agent",
        "status": "running",
        "version": "1.0",
        "message": "Business Analyst Autonomous Agent"
    }

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
    
    return AgentResponse(
        session_id=session_id,
        output=output,
        intent=intent
    )

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
    print("=" * 60)
    print("🚀 BA AGENT STARTING (Simple Version)")
    print("=" * 60)
    print("📡 API: http://localhost:8000")
    print("📚 Interactive Docs: http://localhost:8000/docs")
    print("💡 Try: POST /agent/run with {\"input\":\"I need a login system\", \"user_id\":\"test\"}")
    print("=" * 60)
    print("\n✅ Agent is ready! Press Ctrl+C to stop.\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
