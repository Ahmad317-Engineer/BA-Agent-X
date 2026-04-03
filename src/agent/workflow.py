"""
Agent Workflow - State Machine Implementation
"""

from typing import Dict, Any
from langgraph.graph import StateGraph, END
from src.agent.state import AgentContext, AgentState, IntentType

def understand_node(context: AgentContext) -> AgentContext:
    """Parse user input and identify intent"""
    print(f"[UNDERSTAND] Processing: {context.original_input[:50]}...")
    
    # Simple intent detection (will be replaced with LLM)
    input_lower = context.original_input.lower()
    
    if "requirement" in input_lower or "need" in input_lower or "feature" in input_lower:
        context.intent = IntentType.REQUIREMENTS
    elif "gap" in input_lower or "missing" in input_lower:
        context.intent = IntentType.GAP_ANALYSIS
    elif "document" in input_lower or "write" in input_lower:
        context.intent = IntentType.DOCUMENTATION
    elif "test" in input_lower or "scenario" in input_lower:
        context.intent = IntentType.TESTING
    else:
        context.intent = IntentType.GENERAL
    
    context.extracted_entities = {
        "keywords": input_lower.split(),
        "length": len(context.original_input)
    }
    
    context.update_state(AgentState.RETRIEVING)
    return context

def retrieve_node(context: AgentContext) -> AgentContext:
    """Retrieve relevant documents and context"""
    print(f"[RETRIEVE] Fetching context for intent: {context.intent}")
    
    # Mock retrieval (will connect to ChromaDB later)
    context.retrieved_docs = [
        {"title": "Sample Document", "content": "This is relevant content", "score": 0.95}
    ]
    
    context.update_state(AgentState.ANALYZING)
    return context

def analyze_node(context: AgentContext) -> AgentContext:
    """Perform analysis based on intent"""
    print(f"[ANALYZE] Analyzing for {context.intent}")
    
    if context.intent == IntentType.REQUIREMENTS:
        context.analysis = f"""
        Requirements Analysis for: "{context.original_input}"
        
        Key Findings:
        - User needs identified
        - Impact scope determined
        - Stakeholders affected: End users, System admins
        
        Recommended Approach:
        1. Gather detailed specifications
        2. Create user stories
        3. Define acceptance criteria
        """
    elif context.intent == IntentType.GAP_ANALYSIS:
        context.analysis = f"""
        Gap Analysis for: "{context.original_input}"
        
        Current State: Not implemented
        Desired State: Working solution
        Gaps: Missing functionality, Documentation needed
        
        Recommendations: Implement missing features
        """
    else:
        context.analysis = f"""
        General Analysis for: "{context.original_input}"
        
        Understanding your request. As a Business Analyst, I can help with:
        - Requirements gathering
        - Process improvement
        - Stakeholder alignment
        """
    
    context.update_state(AgentState.DRAFTING)
    return context

def draft_node(context: AgentContext) -> AgentContext:
    """Create draft output based on analysis"""
    print(f"[DRAFT] Creating draft for {context.intent}")
    
    if context.intent == IntentType.REQUIREMENTS:
        context.draft_content = f"""
        # Requirements Document
        
        ## User Story
        As a stakeholder, I want {context.original_input}
        so that business value is delivered.
        
        ## Acceptance Criteria
        1. Feature works as specified
        2. Edge cases are handled
        3. Documentation is updated
        4. Unit tests pass
        
        ## Technical Notes
        - Estimated effort: 3-5 story points
        - Dependencies: None identified
        - Risks: Low
        """
    elif context.intent == IntentType.GAP_ANALYSIS:
        context.draft_content = f"""
        # Gap Analysis Report
        
        ## Summary
        Identified gaps in: {context.original_input}
        
        ## Detailed Findings
        - Gap 1: Missing functionality
        - Gap 2: Documentation outdated
        - Gap 3: Stakeholder alignment needed
        
        ## Action Items
        1. Schedule requirements workshop
        2. Update documentation
        3. Create implementation plan
        """
    else:
        context.draft_content = f"""
        # Business Analysis Response
        
        ## Request: {context.original_input}
        
        ## Response
        {context.analysis}
        
        ## Next Steps
        Please provide more specific details about your requirements
        for a more detailed analysis.
        """
    
    context.update_state(AgentState.VALIDATING)
    return context

def validate_node(context: AgentContext) -> AgentContext:
    """Validate the draft against constraints"""
    print(f"[VALIDATE] Checking draft quality")
    
    # Simple validation
    context.validation_result = {
        "valid": len(context.draft_content) > 100,
        "issues": [] if len(context.draft_content) > 100 else ["Draft too short"]
    }
    
    # Determine if human approval needed
    context.requires_human_approval = len(context.draft_content) > 1000
    
    context.update_state(AgentState.EXECUTING if not context.requires_human_approval else AgentState.REVIEWING)
    return context

def execute_node(context: AgentContext) -> AgentContext:
    """Execute any actions (create tickets, send notifications)"""
    print(f"[EXECUTE] Executing actions for {context.intent}")
    
    # Log the execution
    context.tool_calls_made.append({
        "action": "generate_response",
        "intent": context.intent,
        "timestamp": context.updated_at.isoformat()
    })
    
    context.update_state(AgentState.COMPLETED)
    return context

def review_node(context: AgentContext) -> AgentContext:
    """Wait for human review (placeholder for HITL)"""
    print(f"[REVIEW] Waiting for human approval")
    context.update_state(AgentState.EXECUTING)
    return context

def create_agent_graph():
    """Create and return the LangGraph workflow"""
    
    # Create the graph
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
    
    # Compile the graph
    return workflow.compile()

# For testing
if __name__ == "__main__":
    print("Testing Agent Workflow...")
    agent = create_agent_graph()
    
    test_context = AgentContext(
        session_id="test_123",
        user_id="test_user",
        channel="cli",
        original_input="I need a login feature for my app"
    )
    
    result = agent.invoke(test_context)
    
    print("\n" + "=" * 50)
    print("RESULT:")
    print("=" * 50)
    print(f"State: {result.state}")
    print(f"Intent: {result.intent}")
    print(f"Draft length: {len(result.draft_content)} characters")