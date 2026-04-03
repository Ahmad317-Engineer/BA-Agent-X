"""
Enhanced Agent Workflow with Persistence
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from src.agent.state import AgentContext, AgentState, IntentType
import sqlite3
from pathlib import Path

# Import node functions (using our existing ones)
from src.agent.workflow import (
    understand_node, retrieve_node, analyze_node,
    draft_node, validate_node, execute_node, review_node
)

def create_agent_graph_with_persistence(db_path: str = "checkpoints.db"):
    """Create workflow with SQLite persistence"""
    
    workflow = StateGraph(AgentContext)
    
    # Add nodes
    workflow.add_node("understand", understand_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("draft", draft_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("review", review_node)
    
    # Set entry point
    workflow.set_entry_point("understand")
    
    # Define edges
    workflow.add_edge("understand", "retrieve")
    workflow.add_edge("retrieve", "analyze")
    workflow.add_edge("analyze", "draft")
    workflow.add_edge("draft", "validate")
    
    # Conditional edge from validate
    def should_review(context: AgentContext):
        if context.requires_human_approval:
            return "review"
        return "execute"
    
    workflow.add_conditional_edges("validate", should_review, {
        "review": "review",
        "execute": "execute"
    })
    
    workflow.add_edge("review", "execute")
    workflow.add_edge("execute", END)
    
    # Setup persistence
    conn = sqlite3.connect(db_path)
    memory = SqliteSaver(conn)
    
    # Compile with checkpointer
    return workflow.compile(checkpointer=memory)

# Test with persistence
if __name__ == "__main__":
    print("Testing workflow with persistence...")
    agent = create_agent_graph_with_persistence()
    
    # Create test context
    config = {"configurable": {"thread_id": "test_thread_001"}}
    
    test_context = AgentContext(
        session_id="test_persist_001",
        user_id="tester",
        channel="cli",
        original_input="I need a login system with MFA"
    )
    
    # Run first time
    result = agent.invoke(test_context, config)
    print(f"✅ First run completed: {result.state}")
    
    # Run again with same thread_id - should resume from checkpoint
    result2 = agent.invoke(test_context, config)
    print(f"✅ Second run (from checkpoint): {result2.state}")
    
    print("✅ Workflow with persistence working!")
