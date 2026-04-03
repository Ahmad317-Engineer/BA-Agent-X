"""
Understanding Node Implementation
"""

from src.agent.state import AgentContext, AgentState, IntentType

def understand_node(context: AgentContext) -> AgentContext:
    """Parse user input and identify intent"""
    print(f"[UNDERSTAND] Processing: {context.original_input[:50]}...")
    
    input_lower = context.original_input.lower()
    
    # Intent detection
    if any(word in input_lower for word in ["requirement", "need", "feature", "want"]):
        context.intent = IntentType.REQUIREMENTS
    elif any(word in input_lower for word in ["gap", "missing", "lack"]):
        context.intent = IntentType.GAP_ANALYSIS
    elif any(word in input_lower for word in ["document", "write", "create"]):
        context.intent = IntentType.DOCUMENTATION
    elif any(word in input_lower for word in ["test", "scenario"]):
        context.intent = IntentType.TESTING
    else:
        context.intent = IntentType.GENERAL
    
    # Extract entities
    context.extracted_entities = {
        "keywords": input_lower.split(),
        "length": len(context.original_input),
        "has_question": "?" in context.original_input
    }
    
    context.update_state(AgentState.RETRIEVING)
    return context
