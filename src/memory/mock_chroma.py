"""
Mock ChromaDB Service - For development without Docker
"""

class MockCollection:
    def __init__(self, name):
        self.name = name
        self.documents = []
    
    def add(self, ids=None, embeddings=None, metadatas=None, documents=None):
        print(f"[MOCK CHROMA] Added {len(documents or [])} documents to {self.name}")
        return {"ids": ids or []}
    
    def query(self, query_embeddings, n_results=5):
        print(f"[MOCK CHROMA] Querying with {len(query_embeddings)} embeddings")
        return {
            "ids": [["doc1", "doc2"]],
            "documents": [["Sample document about requirements", "Another relevant doc"]],
            "distances": [[0.1, 0.3]],
            "metadatas": [[{"source": "mock"}, {"source": "mock"}]]
        }

class MockChromaClient:
    def __init__(self, path=None):
        print(f"[MOCK CHROMA] Client initialized")
    
    def get_or_create_collection(self, name):
        return MockCollection(name)
    
    def delete_collection(self, name):
        print(f"[MOCK CHROMA] Deleted collection {name}")

def PersistentClient(path=None):
    return MockChromaClient()

print("✅ Mock ChromaDB loaded (Docker not required)")
