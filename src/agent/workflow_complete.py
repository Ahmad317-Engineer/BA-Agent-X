"""
Complete Agent Workflow - Integrates all nodes
"""

from langgraph.graph import StateGraph, END
from src.agent.state import AgentContext
from src.agent.nodes.understand import understand_node
from src.agent.nodes.retrieve import retrieve_node
from src.agent.nodes.analysis import analyze_node
from src.agent.nodes.draft import draft_node
from src.agent.nodes.validate import validate_node
from src.agent.nodes.execute import execute_node, review_node

def create_complete_agent():
    """Create the complete agent workflow"""
    
    workflow = StateGraph(AgentContext)
    
    # Add all nodes
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
    
    # Conditional edge based on approval
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
    
    return workflow.compile()

# Test the complete agent
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Complete Agent Workflow")
    print("=" * 60)
    
    agent = create_complete_agent()
    
    test_cases = [
        "I need a login feature for my web app",
        "We are missing inventory tracking",
        "Please document the API endpoints"
    ]
    
    for test_input in test_cases:
        print(f"\n📝 Input: {test_input}")
        print("-" * 40)
        
        context = AgentContext(
            session_id=f"test_{hash(test_input)}",
            user_id="tester",
            channel="cli",
            original_input=test_input
        )
        
        result = agent.invoke(context)
        print(f"\n✅ Result: {result.state}")
        print(f"   Intent: {result.intent}")
        print(f"   Draft length: {len(result.draft_content) if result.draft_content else 0}")
        if result.validation_result:
            print(f"   Valid: {result.validation_result.get('valid')}")
    
    print("\n" + "=" * 60)
    print("✅ Complete Agent Workflow Test Passed!")
