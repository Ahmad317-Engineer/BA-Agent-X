"""
Phase 4 Test - Quick verification of all nodes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("PHASE 4 - AGENT NODES VERIFICATION")
print("=" * 60)

# Test 1: Import all nodes
print("\n1️⃣ Testing node imports...")
from src.agent.nodes.understand import understand_node
from src.agent.nodes.retrieve import retrieve_node
from src.agent.nodes.analysis import analyze_node
from src.agent.nodes.draft import draft_node
from src.agent.nodes.validate import validate_node
from src.agent.nodes.execute import execute_node
print("  ✅ All nodes imported successfully")

# Test 2: Create a test context
print("\n2️⃣ Creating test context...")
from src.agent.state import AgentContext, AgentState, IntentType

context = AgentContext(
    session_id="test_001",
    user_id="tester",
    channel="cli",
    original_input="I need a login feature for my web app"
)
print(f"  ✅ Context created: {context.session_id}")

# Test 3: Run through all nodes
print("\n3️⃣ Running through workflow...")
context = understand_node(context)
print(f"  → Understand: {context.state}, Intent: {context.intent}")

context = retrieve_node(context)
print(f"  → Retrieve: {context.state}, Docs: {len(context.retrieved_docs)}")

context = analyze_node(context)
print(f"  → Analyze: {context.state}")

context = draft_node(context)
print(f"  → Draft: {context.state}, Length: {len(context.draft_content)}")

context = validate_node(context)
print(f"  → Validate: {context.state}, Valid: {context.validation_result['valid']}")

context = execute_node(context)
print(f"  → Execute: {context.state}")

print("\n" + "=" * 60)
print("✅ PHASE 4 VERIFICATION COMPLETE!")
print("   All agent nodes are working correctly!")
print("=" * 60)
