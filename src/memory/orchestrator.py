"""
Memory Orchestrator - Fixed version
"""

from typing import List, Dict, Any, Optional
from src.memory.vector_memory import VectorMemory
from src.memory.graph_memory import SystemGraph
import hashlib
from datetime import datetime

class MemoryOrchestrator:
    """Coordinates vector and graph memory for intelligent retrieval"""
    
    def __init__(self, persist_dir: str = "./data"):
        self.vector_memory = VectorMemory(persist_dir=f"{persist_dir}/vectors")
        self.graph_memory = SystemGraph(persist_dir=f"{persist_dir}/graph")
        self.cache = {}
        self.cache_ttl = 300
    
    def _get_cache_key(self, query: str) -> str:
        return hashlib.md5(query.encode()).hexdigest()
    
    def _is_cached(self, key: str) -> bool:
        if key in self.cache:
            timestamp, _ = self.cache[key]
            age = (datetime.now() - timestamp).total_seconds()
            return age < self.cache_ttl
        return False
    
    def add_business_document(self, content: str, title: str, doc_type: str, 
                              related_systems: List[str] = None):
        """Add a business document to memory"""
        metadata = {
            'title': title,
            'type': doc_type,
            'related_systems': related_systems or [],
            'timestamp': datetime.now().isoformat()
        }
        
        doc_id = self.vector_memory.add_document(content, metadata)
        
        # Add systems to graph if they don't exist
        if related_systems:
            for system in related_systems:
                if not self.graph_memory.get_system_info(system):
                    self.graph_memory.add_system(system, "business_system", {})
        
        return doc_id
    
    def hybrid_search(self, query: str, include_graph: bool = True) -> Dict[str, Any]:
        """Perform hybrid search across vector and graph memory"""
        
        cache_key = self._get_cache_key(query)
        if self._is_cached(cache_key):
            print(f"📦 Returning cached result for: {query[:50]}...")
            return self.cache[cache_key][1]
        
        result = {
            'query': query,
            'vector_results': [],
            'graph_results': [],
            'combined_insights': []
        }
        
        # 1. Vector search for relevant documents
        print(f"🔍 Vector search for: {query[:50]}...")
        vector_results = self.vector_memory.search(query, n_results=5)
        result['vector_results'] = vector_results
        
        # 2. Extract system names from vector results
        mentioned_systems = set()
        for vr in vector_results:
            systems = vr['metadata'].get('related_systems', [])
            mentioned_systems.update(systems)
        
        # 3. Graph search for impacted systems
        if include_graph and mentioned_systems:
            print(f"🔗 Graph analysis for systems: {mentioned_systems}")
            for system in mentioned_systems:
                impact = self.graph_memory.get_downstream_impact(system)
                if impact:
                    result['graph_results'].append({
                        'system': system,
                        'downstream': impact
                    })
        
        # 4. Generate combined insights
        if result['vector_results']:
            result['combined_insights'] = self._generate_insights(result)
        
        # Cache the result
        self.cache[cache_key] = (datetime.now(), result)
        
        return result
    
    def _generate_insights(self, search_result: Dict) -> List[str]:
        """Generate insights from combined search results"""
        insights = []
        
        # Document insights
        doc_count = len(search_result['vector_results'])
        insights.append(f"Found {doc_count} relevant documents")
        
        # Top document
        if search_result['vector_results']:
            top_doc = search_result['vector_results'][0]
            insights.append(f"Most relevant: {top_doc['metadata'].get('title', 'Untitled')}")
        
        # System impact insights
        if search_result.get('graph_results'):
            systems = [g['system'] for g in search_result['graph_results']]
            insights.append(f"Systems impacted: {', '.join(systems)}")
            
            total_downstream = sum(len(g['downstream']) for g in search_result['graph_results'])
            insights.append(f"Total downstream dependencies: {total_downstream}")
        
        return insights
    
    def add_sample_data(self):
        """Add sample business documents for testing"""
        print("📚 Adding sample business documents...")
        
        # First, ensure systems exist in graph
        systems = ["CRM", "ERP", "BI", "Warehouse", "API Gateway"]
        for system in systems:
            if not self.graph_memory.get_system_info(system):
                self.graph_memory.add_system(system, "business_system", {})
        
        # Add sample connections between systems
        connections = [
            ("CRM", "ERP", "data_sync", "bidirectional"),
            ("ERP", "Warehouse", "inventory_feed", "one-way"),
            ("Warehouse", "BI", "reporting", "one-way"),
            ("API Gateway", "CRM", "api_calls", "bidirectional"),
            ("API Gateway", "ERP", "api_calls", "bidirectional")
        ]
        
        for from_sys, to_sys, conn_type, flow in connections:
            try:
                self.graph_memory.add_connection(from_sys, to_sys, conn_type, flow)
            except ValueError:
                pass  # Connection might already exist
        
        # Add documents
        samples = [
            {
                "content": """
                User Authentication System Requirements:
                - Login with email/password
                - Multi-factor authentication support
                - Password reset workflow
                - Session management with JWT tokens
                - OAuth2 integration with Google and Microsoft
                """,
                "title": "Authentication Requirements",
                "type": "requirements",
                "systems": ["CRM", "API Gateway"]
            },
            {
                "content": """
                Inventory Management System Specifications:
                - Real-time stock tracking
                - Automatic reorder points
                - Warehouse location management
                - Integration with ERP for purchasing
                - Reporting dashboard for BI
                """,
                "title": "Inventory Management Specs",
                "type": "specification",
                "systems": ["Warehouse", "ERP", "BI"]
            },
            {
                "content": """
                API Gateway Documentation:
                - Rate limiting and throttling
                - Request/response transformation
                - Authentication middleware
                - Service discovery integration
                - Monitoring and logging setup
                """,
                "title": "API Gateway Documentation",
                "type": "documentation",
                "systems": ["API Gateway", "CRM", "ERP"]
            }
        ]
        
        for sample in samples:
            self.add_business_document(
                content=sample['content'],
                title=sample['title'],
                doc_type=sample['type'],
                related_systems=sample['systems']
            )
        
        print("✅ Sample data added!")

# Test the fixed orchestrator
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Memory Orchestrator (Fixed)")
    print("=" * 60)
    
    mo = MemoryOrchestrator()
    mo.add_sample_data()
    
    test_queries = [
        "authentication system",
        "inventory tracking",
        "API gateway"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 40)
        result = mo.hybrid_search(query)
        
        print(f"\n📊 Results:")
        print(f"  Vector matches: {len(result['vector_results'])}")
        for vr in result['vector_results'][:2]:
            print(f"    - {vr['metadata']['title']} (score: {vr['similarity']:.3f})")
        
        if result.get('graph_results'):
            print(f"  Graph insights: {len(result['graph_results'])} systems affected")
        
        if result.get('combined_insights'):
            print(f"  💡 Insights:")
            for insight in result['combined_insights']:
                print(f"    - {insight}")
    
    print("\n" + "=" * 60)
    print("✅ Memory Orchestrator test complete!")
