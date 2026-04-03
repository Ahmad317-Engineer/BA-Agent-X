"""
Mock Neo4j Service - For development without Docker
"""

class MockNeo4jDriver:
    """Mock Neo4j driver for testing"""
    
    class Session:
        def run(self, query, **parameters):
            print(f"[MOCK NEO4J] Query: {query}")
            return MockResult()
        
        def close(self):
            pass
    
    def session(self):
        return self.Session()
    
    def close(self):
        pass
    
    def verify_connectivity(self):
        print("[MOCK NEO4J] Connection verified")
        return True

class MockResult:
    def data(self):
        return [{"system": "CRM", "type": "database", "dependencies": ["ERP", "BI"]}]
    
    def single(self):
        return MockRecord()

class MockRecord:
    def get(self, key, default=None):
        if key == "systems":
            return ["CRM", "ERP", "Warehouse"]
        return []

def GraphDatabase():
    return MockNeo4jDriver()

print("✅ Mock Neo4j loaded (Docker not required)")
