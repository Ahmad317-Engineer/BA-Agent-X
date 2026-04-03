"""
Draft Node - Create draft output
"""

from src.agent.state import AgentContext, AgentState, IntentType

def draft_node(context: AgentContext) -> AgentContext:
    """Create draft output based on analysis"""
    print(f"[DRAFT] Creating draft for {context.intent}")
    
    if context.intent == IntentType.REQUIREMENTS:
        context.draft_content = f"""
# Requirements Document

## User Story
As a stakeholder, I want {context.original_input} so that business value is delivered.

## Acceptance Criteria
1. Feature works as specified
2. Edge cases are handled
3. Documentation is updated
4. Unit tests pass

## Technical Notes
- Estimated effort: 3-5 story points
- Dependencies: None identified
- Risks: Low

## Analysis
{context.analysis if context.analysis else 'Analysis in progress...'}
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

## Analysis
{context.analysis if context.analysis else 'Gap analysis in progress...'}
"""
    else:
        context.draft_content = f"""
# Business Analysis Response

## Request: {context.original_input}

## Response
{context.analysis if context.analysis else 'Analyzing your request...'}

## Next Steps
Please provide more specific details about your requirements for a more detailed analysis.
"""
    
    context.update_state(AgentState.VALIDATING)
    return context
