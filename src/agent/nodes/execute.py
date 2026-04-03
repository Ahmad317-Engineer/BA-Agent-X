"""
Execute Node - Execute actions
"""

from src.agent.state import AgentContext, AgentState, IntentType

def execute_node(context: AgentContext) -> AgentContext:
    """Execute actions (create tickets, send notifications)"""
    print(f"[EXECUTE] Executing actions for {context.intent}")
    
    # Log execution
    context.tool_calls_made.append({
        "action": "generate_response",
        "intent": context.intent.value if context.intent else "unknown",
        "timestamp": context.updated_at.isoformat(),
        "draft_length": len(context.draft_content) if context.draft_content else 0
    })
    
    context.update_state(AgentState.COMPLETED)
    return context

def review_node(context: AgentContext) -> AgentContext:
    """Wait for human review"""
    print(f"[REVIEW] Waiting for human approval")
    # Auto-approve for now
    context.update_state(AgentState.EXECUTING)
    return context
