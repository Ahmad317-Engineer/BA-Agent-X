"""
Validate Node - Validate draft quality
"""

from src.agent.state import AgentContext, AgentState

def validate_node(context: AgentContext) -> AgentContext:
    """Validate the draft against constraints"""
    print(f"[VALIDATE] Checking draft quality")
    
    issues = []
    
    # Check draft length
    if not context.draft_content or len(context.draft_content) < 100:
        issues.append("Draft too short")
    
    # Check if it has required sections
    if context.draft_content:
        has_sections = any(section in context.draft_content for section in ["#", "##"])
        if not has_sections:
            issues.append("Missing markdown sections")
    
    context.validation_result = {
        "valid": len(issues) == 0,
        "issues": issues,
        "draft_length": len(context.draft_content) if context.draft_content else 0
    }
    
    # Determine if human approval needed
    context.requires_human_approval = len(context.draft_content) > 2000 if context.draft_content else False
    
    context.update_state(AgentState.EXECUTING if not context.requires_human_approval else AgentState.REVIEWING)
    return context
