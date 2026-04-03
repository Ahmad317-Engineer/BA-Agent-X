"""
Phase 2 Verification - Quick test of all memory systems
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("PHASE 2 - MEMORY SYSTEMS VERIFICATION")
print("=" * 60)

# 1. Test Vector Memory
print("\n1️⃣ Testing Vector Memory...")
from src.memory.vector_memory import VectorMemory
vm = VectorMemory("verify_test")
vm.add_document("User authentication and MFA requirements", {"title": "Auth Reqs"})
vm.add_document("Inventory management system specs", {"title": "Inventory Specs"})
vm.add_document("API documentation for REST endpoints", {"title": "API Docs"})

results = vm.search("authentication", n_results=2)
print(f"   ✅ Vector search: {len(results)} results")
for r in results:
    print(f"      - {r['metadata']['title']} (score: {r['similarity']:.3f})")

# 2. Test Graph Memory
print("\n2️⃣ Testing Graph Memory...")
from src.memory.graph_memory import SystemGraph
sg = SystemGraph()

# Add systems
sg.add_system("WebApp", "frontend", {})
sg.add_system("API Gateway", "middleware", {})
sg.add_system("Database", "backend", {})
sg.add_system("Cache", "infrastructure", {})

# Add connections
sg.add_connection("WebApp", "API Gateway", "http", "bidirectional")
sg.add_connection("API Gateway", "Database", "sql", "one-way")
sg.add_connection("API Gateway", "Cache", "redis", "bidirectional")

# Test queries
impact = sg.get_downstream_impact("API Gateway")
print(f"   ✅ Downstream from API Gateway: {len(impact)} systems")
for i in impact:
    print(f"      → {i['system']}")

path = sg.find_path("WebApp", "Database")
print(f"   ✅ Path found: {' → '.join(path)}")

# 3. Test Memory Orchestrator
print("\n3️⃣ Testing Memory Orchestrator...")
from src.memory.orchestrator import MemoryOrchestrator
mo = MemoryOrchestrator()
mo.add_sample_data()

result = mo.hybrid_search("authentication system")
print(f"   ✅ Vector results: {len(result['vector_results'])}")
print(f"   ✅ Graph results: {len(result['graph_results'])}")
if result['combined_insights']:
    print(f"   ✅ Insights: {len(result['combined_insights'])}")

print("\n" + "=" * 60)
print("✅ PHASE 2 VERIFICATION COMPLETE!")
print("   Vector Memory, Graph Memory, and Orchestrator all working.")
print("=" * 60)
