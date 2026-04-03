"""
Retrieval Node - Fetch relevant documents and context
"""

from src.agent.state import AgentContext, AgentState
from src.memory.orchestrator import MemoryOrchestrator

# Initialize memory orchestrator
try:
    memory_orchestrator = MemoryOrchestrator()
except Exception as e:
    print(f"Warning: Could not initialize MemoryOrchestrator: {e}")
    memory_orchestrator = None

def retrieve_node(context: AgentContext) -> AgentContext:
    """Retrieve relevant documents and system context"""
    print(f"[RETRIEVE] Fetching context for intent: {context.intent}")
    
    if memory_orchestrator:
        try:
            # Perform hybrid search
            search_result = memory_orchestrator.hybrid_search(context.original_input)
            
            # Store retrieved documents
            context.retrieved_docs = search_result.get('vector_results', [])
            
            # Store graph results if any
            if search_result.get('graph_results'):
                context.system_topology = {
                    'impacted_systems': search_result['graph_results']
                }
        except Exception as e:
            print(f"Search error: {e}")
            context.retrieved_docs = []
    else:
        context.retrieved_docs = []
    
    print(f"  Retrieved {len(context.retrieved_docs)} documents")
    if context.system_topology:
        print(f"  Found {len(context.system_topology.get('impacted_systems', []))} system impacts")
    
    context.update_state(AgentState.ANALYZING)
    return context
