"""
Unit tests for State Machine
Run with: pytest tests/test_state.py -v
"""

import pytest
from datetime import datetime
from src.agent.state import AgentContext, AgentState, IntentType

def test_agent_context_creation():
    """Test that AgentContext creates properly"""
    context = AgentContext(
        session_id="test_001",
        user_id="user_001",
        channel="api",
        original_input="I need a login feature"
    )
    
    assert context.session_id == "test_001"
    assert context.user_id == "user_001"
    assert context.state == AgentState.IDLE
    assert context.intent is None
    assert context.draft_content is None

def test_state_transition():
    """Test state transitions"""
    context = AgentContext(
        session_id="test_002",
        user_id="user_002",
        channel="cli",
        original_input="Test input"
    )
    
    old_time = context.updated_at
    context.update_state(AgentState.UNDERSTANDING)
    
    assert context.state == AgentState.UNDERSTANDING
    assert context.updated_at > old_time

def test_intent_types():
    """Test all intent types"""
    context = AgentContext(
        session_id="test_003",
        user_id="user_003",
        channel="api",
        original_input="Requirements for login"
    )
    
    context.intent = IntentType.REQUIREMENTS
    assert context.intent == IntentType.REQUIREMENTS
    
    context.intent = IntentType.GAP_ANALYSIS
    assert context.intent == IntentType.GAP_ANALYSIS
    
    context.intent = IntentType.DOCUMENTATION
    assert context.intent == IntentType.DOCUMENTATION

def test_retrieved_docs():
    """Test document retrieval storage"""
    context = AgentContext(
        session_id="test_004",
        user_id="user_004",
        channel="api",
        original_input="Test"
    )
    
    docs = [
        {"title": "Doc1", "content": "Content1", "score": 0.95},
        {"title": "Doc2", "content": "Content2", "score": 0.87}
    ]
    context.retrieved_docs = docs
    
    assert len(context.retrieved_docs) == 2
    assert context.retrieved_docs[0]["title"] == "Doc1"

if __name__ == "__main__":
    print("Running state machine tests...")
    test_agent_context_creation()
    test_state_transition()
    test_intent_types()
    test_retrieved_docs()
    print("✅ All state machine tests passed!")
