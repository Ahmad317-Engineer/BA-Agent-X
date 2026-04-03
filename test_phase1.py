"""
Phase 1 Complete Test Suite
Tests all foundational components
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all imports work"""
    print("\n📦 Testing imports...")
    imports = [
        ("src.agent.state", "State Machine"),
        ("src.agent.workflow", "Workflow"),
        ("src.llm.gateway", "LLM Gateway"),
        ("src.memory.mock_neo4j", "Mock Neo4j"),
        ("src.memory.mock_chroma", "Mock ChromaDB"),
        ("src.llm.mock_ollama", "Mock Ollama")
    ]
    
    results = []
    for module, name in imports:
        try:
            __import__(module)
            print(f"  ✅ {name}")
            results.append(True)
        except Exception as e:
            print(f"  ❌ {name}: {e}")
            results.append(False)
    
    return all(results)

def test_llm_gateway():
    """Test LLM gateway functionality"""
    print("\n🤖 Testing LLM Gateway...")
    from src.llm.gateway import get_llm
    
    llm = get_llm("mock")
    response = llm.generate("What is a user story?")
    
    assert len(response) > 50
    print(f"  ✅ Mock LLM response: {response[:100]}...")
    return True

def test_state_machine():
    """Test state machine functionality"""
    print("\n🔄 Testing State Machine...")
    from src.agent.state import AgentContext, AgentState, IntentType
    
    context = AgentContext(
        session_id="test",
        user_id="user",
        channel="cli",
        original_input="Test input"
    )
    
    assert context.state == AgentState.IDLE
    context.update_state(AgentState.ANALYZING)
    assert context.state == AgentState.ANALYZING
    
    context.intent = IntentType.REQUIREMENTS
    assert context.intent == IntentType.REQUIREMENTS
    
    print("  ✅ State transitions working")
    return True

def test_workflow():
    """Test workflow execution"""
    print("\n⚙️ Testing Workflow...")
    from src.agent.workflow import create_agent_graph
    from src.agent.state import AgentContext
    
    agent = create_agent_graph()
    
    test_context = AgentContext(
        session_id="test_workflow",
        user_id="tester",
        channel="cli",
        original_input="I need a login system"
    )
    
    result = agent.invoke(test_context)
    
    assert result.draft_content is not None
    assert len(result.draft_content) > 100
    print(f"  ✅ Workflow completed: {result.state}")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 1 - COMPLETE TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("LLM Gateway", test_llm_gateway),
        ("State Machine", test_state_machine),
        ("Workflow", test_workflow)
    ]
    
    passed = 0
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  ❌ {name} failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("✅ PHASE 1 COMPLETE! Ready for Phase 2.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
    print("=" * 60)
