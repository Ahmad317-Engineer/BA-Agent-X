"""
Graph Memory System - System topology and relationships
"""

from typing import List, Dict, Any, Optional
import json
from pathlib import Path

class SystemGraph:
    """Graph database for system relationships and dependencies"""
    
    def __init__(self, persist_dir: str = "./data/graphdb"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory graph storage
        self.systems = {}  # system_name -> system_data
        self.connections = []  # list of (from, to, type, data_flow)
        
        self._load_graph()
    
    def _load_graph(self):
        """Load graph from disk"""
        graph_file = self.persist_dir / "graph_data.json"
        if graph_file.exists():
            with open(graph_file, 'r') as f:
                data = json.load(f)
                self.systems = data.get('systems', {})
                self.connections = data.get('connections', [])
                print(f"✅ Loaded {len(self.systems)} systems and {len(self.connections)} connections")
    
    def _save_graph(self):
        """Save graph to disk"""
        graph_file = self.persist_dir / "graph_data.json"
        with open(graph_file, 'w') as f:
            json.dump({
                'systems': self.systems,
                'connections': self.connections
            }, f, indent=2)
    
    def add_system(self, name: str, system_type: str, metadata: Dict[str, Any]):
        """Add a system/node to the graph"""
        self.systems[name] = {
            'name': name,
            'type': system_type,
            'metadata': metadata,
            'created_at': str(Path(__file__).stat().st_mtime)
        }
        self._save_graph()
        print(f"🖥️ Added system: {name} ({system_type})")
    
    def add_connection(self, from_system: str, to_system: str, 
                       connection_type: str, data_flow: str = "bidirectional"):
        """Add a connection/edge between systems"""
        # Validate systems exist
        if from_system not in self.systems:
            raise ValueError(f"System '{from_system}' not found")
        if to_system not in self.systems:
            raise ValueError(f"System '{to_system}' not found")
        
        connection = {
            'from': from_system,
            'to': to_system,
            'type': connection_type,
            'data_flow': data_flow
        }
        self.connections.append(connection)
        self._save_graph()
        print(f"🔗 Added connection: {from_system} -> {to_system} ({connection_type})")
    
    def get_downstream_impact(self, system_name: str) -> List[Dict]:
        """Get all systems that depend on the given system"""
        impacted = []
        visited = set()
        
        def traverse(current: str):
            if current in visited:
                return
            visited.add(current)
            
            for conn in self.connections:
                if conn['from'] == current:
                    impacted.append({
                        'system': conn['to'],
                        'connection': conn,
                        'path': f"{system_name} -> {conn['to']}"
                    })
                    traverse(conn['to'])
        
        traverse(system_name)
        return impacted
    
    def get_upstream_dependencies(self, system_name: str) -> List[Dict]:
        """Get all systems that the given system depends on"""
        dependencies = []
        
        for conn in self.connections:
            if conn['to'] == system_name:
                dependencies.append({
                    'system': conn['from'],
                    'connection': conn,
                    'type': conn['type']
                })
        
        return dependencies
    
    def get_system_info(self, system_name: str) -> Optional[Dict]:
        """Get information about a specific system"""
        return self.systems.get(system_name)
    
    def get_all_systems(self) -> List[str]:
        """Get all system names"""
        return list(self.systems.keys())
    
    def find_path(self, from_system: str, to_system: str) -> List[str]:
        """Find a path between two systems (BFS)"""
        if from_system not in self.systems or to_system not in self.systems:
            return []
        
        from collections import deque
        queue = deque([(from_system, [from_system])])
        visited = set()
        
        while queue:
            current, path = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            
            for conn in self.connections:
                if conn['from'] == current:
                    if conn['to'] == to_system:
                        return path + [conn['to']]
                    queue.append((conn['to'], path + [conn['to']]))
        
        return []

# Test the graph memory
if __name__ == "__main__":
    print("=" * 50)
    print("Testing Graph Memory System")
    print("=" * 50)
    
    # Initialize
    sg = SystemGraph()
    
    # Add systems
    sample_systems = [
        ("CRM", "database", {"vendor": "Salesforce", "version": "2024"}),
        ("ERP", "enterprise", {"vendor": "SAP", "version": "S/4HANA"}),
        ("Warehouse", "application", {"vendor": "In-house", "type": "inventory"}),
        ("BI", "analytics", {"vendor": "Tableau", "version": "2024.1"}),
        ("API Gateway", "middleware", {"vendor": "Kong", "version": "3.0"})
    ]
    
    for name, sys_type, metadata in sample_systems:
        sg.add_system(name, sys_type, metadata)
    
    # Add connections
    connections = [
        ("CRM", "ERP", "data_sync", "bidirectional"),
        ("ERP", "Warehouse", "inventory_feed", "one-way"),
        ("Warehouse", "BI", "reporting", "one-way"),
        ("API Gateway", "CRM", "api_calls", "bidirectional"),
        ("API Gateway", "ERP", "api_calls", "bidirectional")
    ]
    
    for from_sys, to_sys, conn_type, flow in connections:
        sg.add_connection(from_sys, to_sys, conn_type, flow)
    
    # Test queries
    print("\n🔍 Downstream impact of ERP:")
    impact = sg.get_downstream_impact("ERP")
    for i in impact:
        print(f"  → {i['system']} via {i['connection']['type']}")
    
    print("\n🔍 Upstream dependencies of BI:")
    deps = sg.get_upstream_dependencies("BI")
    for d in deps:
        print(f"  ← {d['system']} via {d['connection']['type']}")
    
    print("\n🔍 Path from API Gateway to BI:")
    path = sg.find_path("API Gateway", "BI")
    print(f"  {' → '.join(path)}")
    
    print("\n✅ Graph Memory test complete!")
