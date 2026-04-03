"""
Analysis Node - Perform analysis based on intent
"""

from src.agent.state import AgentContext, AgentState, IntentType

def analyze_node(context: AgentContext) -> AgentContext:
    """Perform analysis based on intent and retrieved context"""
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
