"""
BA Agent API - With State Machine
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import uuid
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agent.state import AgentContext
from src.agent.workflow import create_agent_graph

app = FastAPI(
    title="BA Agent - Business Analyst Autonomous Agent",
    description="AI agent that acts as a real Business Analyst",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent_graph = create_agent_graph()
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


def extract_context(result):
    """LangGraph's invoke() can return the state object directly, or a dict-like
    AddableValuesDict containing it. Find the actual AgentContext instance."""
    if isinstance(result, AgentContext):
        return result
    if isinstance(result, dict):
        # Direct key match
        if "context" in result and isinstance(result["context"], AgentContext):
            return result["context"]
        # Search all values for an AgentContext instance
        for v in result.values():
            if isinstance(v, AgentContext):
                return v
        # As a last resort: maybe the dict IS the state fields themselves
        # (LangGraph sometimes returns the Pydantic model's __dict__ as AddableValuesDict)
        try:
            return AgentContext(**result)
        except Exception:
            pass
    raise ValueError(f"Could not extract AgentContext from LangGraph result: {type(result)} - {result}")


@app.get("/")
async def root():
    return {"agent": "BA Agent v2", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "2.0.0"}


@app.get("/ui")
async def frontend():
    return FileResponse("frontend/index.html")


@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: UserRequest):
    session_id = str(uuid.uuid4())
    context = AgentContext(
        session_id=session_id,
        user_id=request.user_id,
        channel=request.channel,
        original_input=request.input
    )
    try:
        result = agent_graph.invoke(context)
        ctx = extract_context(result)

        sessions[session_id] = {
            "user_id": request.user_id,
            "input": request.input,
            "intent": ctx.intent.value if ctx.intent else "unknown",
            "output": ctx.draft_content,
            "status": ctx.state.value,
            "created_at": ctx.created_at.isoformat(),
            "updated_at": ctx.updated_at.isoformat()
        }

        return AgentResponse(
            session_id=session_id,
            status=ctx.state.value,
            intent=ctx.intent.value if ctx.intent else "unknown",
            output=ctx.draft_content or "Processing complete",
            needs_approval=ctx.requires_human_approval,
            error=ctx.error
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
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]


@app.get("/agent/sessions")
async def list_sessions(limit: int = 10):
    recent_sessions = list(sessions.keys())[-limit:]
    return {"total": len(sessions), "sessions": recent_sessions, "limit": limit}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)