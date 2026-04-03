"""
Agent State Machine Definition
"""

from enum import Enum
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class AgentState(str, Enum):
    """Possible states for the BA Agent"""
    IDLE = "idle"
    UNDERSTANDING = "understanding"      # Parsing input
    RETRIEVING = "retrieving"            # Fetching context
    ANALYZING = "analyzing"              # LLM reasoning
    DRAFTING = "drafting"                # Creating artifacts
    VALIDATING = "validating"            # Checking constraints
    EXECUTING = "executing"              # Using tools
    REVIEWING = "reviewing"              # Human approval
    COMPLETED = "completed"
    ERROR = "error"

class IntentType(str, Enum):
    REQUIREMENTS = "requirements_elicitation"
    GAP_ANALYSIS = "gap_analysis"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    GENERAL = "general"

class AgentContext(BaseModel):
    """Context passed through the agent workflow"""
    session_id: str
    state: AgentState = AgentState.IDLE
    user_id: str
    channel: str
    original_input: str
    
    # Extracted information
    intent: Optional[IntentType] = None
    extracted_entities: Dict[str, Any] = {}
    
    # Retrieved data
    retrieved_docs: List[Dict] = []
    retrieved_tickets: List[Dict] = []
    system_topology: Optional[Dict] = None
    
    # Analysis and output
    analysis: Optional[str] = None
    draft_content: Optional[str] = None
    validation_result: Optional[Dict] = None
    
    # Execution tracking
    tool_calls_made: List[Dict] = []
    requires_human_approval: bool = False
    human_feedback: Optional[str] = None
    
    # Error handling
    error: Optional[str] = None
    
    # Timestamps
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    
    def update_state(self, new_state: AgentState):
        self.state = new_state
        self.updated_at = datetime.now()