"""
Phase 2 Test Suite - Memory Systems
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_vector_memory():
    print("\n📚 Testing Vector Memory...")
    from src.memory.vector_memory import VectorMemory
    
    vm = VectorMemory("phase2_test")
    
    # Add documents
    docs = [
        ("User login and authentication requirements", {"type": "req"}),
        ("Inventory tracking system specs", {"type": "spec"}),
        ("API documentation for REST endpoints", {"type": "docs"})
    ]
    
    for content, metadata in docs:
        vm.add_document(content, metadata)
    
    # Search
    results = vm.search("login", n_results=2)
    assert len(results) > 0
    print(f"  ✅ Vector search found {len(results)} results")
    
    # Cleanup
    for doc_id in list(vm.documents.keys()):
        vm.delete_document(doc_id)
    
    return True

def test_graph_memory():
    print("\n🕸️ Testing Graph Memory...")
    from src.memory.graph_memory import SystemGraph
    
    sg = SystemGraph()
    
    # Add systems
    sg.add_system("CRM", "database", {})
    sg.add_system("ERP", "enterprise", {})
    sg.add_system("BI", "analytics", {})
    
    # Add connections
    sg.add_connection("CRM", "ERP", "sync", "bidirectional")
    sg.add_connection("ERP", "BI", "report", "one-way")
    
    # Test queries
    impact = sg.get_downstream_impact("CRM")
    assert len(impact) >= 1
    print(f"  ✅ Found {len(impact)} downstream dependencies")
    
    path = sg.find_path("CRM", "BI")
    assert len(path) > 0
    print(f"  ✅ Path found: {' → '.join(path)}")
    
    return True

def test_memory_orchestrator():
    print("\n🎯 Testing Memory Orchestrator...")
    from src.memory.orchestrator import MemoryOrchestrator
    
    mo = MemoryOrchestrator()
    mo.add_sample_data()
    
    # Test hybrid search
    result = mo.hybrid_search("authentication")
    assert len(result['vector_results']) > 0
    print(f"  ✅ Found {len(result['vector_results'])} vector results")
    
    if result['graph_results']:
        print(f"  ✅ Found {len(result['graph_results'])} graph impacts")
    
    if result['combined_insights']:
        print(f"  ✅ Generated {len(result['combined_insights'])} insights")
    
    return True

def test_persistence():
    print("\n💾 Testing Persistence...")
    from src.memory.vector_memory import VectorMemory
    
    # Create and add data
    vm1 = VectorMemory("persist_test")
    vm1.add_document("Test content for persistence", {"test": True})
    doc_count_1 = len(vm1.documents)
    
    # Create new instance (should load from disk)
    vm2 = VectorMemory("persist_test")
    doc_count_2 = len(vm2.documents)
    
    assert doc_count_1 == doc_count_2
    print(f"  ✅ Data persisted: {doc_count_1} documents saved and loaded")
    
    # Cleanup
    for doc_id in list(vm1.documents.keys()):
        vm1.delete_document(doc_id)
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 2 - MEMORY SYSTEMS TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Vector Memory", test_vector_memory),
        ("Graph Memory", test_graph_memory),
        ("Memory Orchestrator", test_memory_orchestrator),
        ("Persistence", test_persistence)
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
        print("✅ PHASE 2 COMPLETE! Ready for Phase 3 (Tool Integration).")
    else:
        print("⚠️ Some tests failed. Review errors above.")
    print("=" * 60)
