"""
Tool Registry - Register and manage agent tools
"""

from typing import Dict, Any, Callable, List, Optional
import inspect
from datetime import datetime
import hashlib

class ToolRegistry:
    """Registry for managing agent tools/functions"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.execution_log: List[Dict] = []
    
    def register(self, name: str = None, description: str = None, 
                 requires_approval: bool = False):
        """Decorator to register a tool"""
        def decorator(func: Callable):
            tool_name = name or func.__name__
            self.tools[tool_name] = {
                'function': func,
                'description': description or func.__doc__ or "No description",
                'signature': str(inspect.signature(func)),
                'requires_approval': requires_approval,
                'registered_at': datetime.now().isoformat(),
                'call_count': 0
            }
            return func
        return decorator
    
    def execute(self, tool_name: str, user_id: str, **kwargs) -> Dict[str, Any]:
        """Execute a registered tool"""
        if tool_name not in self.tools:
            return {
                'success': False,
                'error': f"Tool '{tool_name}' not found",
                'available_tools': list(self.tools.keys())
            }
        
        tool = self.tools[tool_name]
        
        # Log execution
        log_entry = {
            'tool': tool_name,
            'user_id': user_id,
            'params': kwargs,
            'timestamp': datetime.now().isoformat(),
            'requires_approval': tool['requires_approval']
        }
        
        try:
            # Execute the tool
            result = tool['function'](**kwargs)
            
            # Update call count
            tool['call_count'] += 1
            
            log_entry['success'] = True
            log_entry['result'] = str(result)[:500]  # Truncate for log
            
            self.execution_log.append(log_entry)
            
            return {
                'success': True,
                'result': result,
                'tool': tool_name,
                'requires_approval': tool['requires_approval']
            }
            
        except Exception as e:
            log_entry['success'] = False
            log_entry['error'] = str(e)
            self.execution_log.append(log_entry)
            
            return {
                'success': False,
                'error': str(e),
                'tool': tool_name
            }
    
    def get_tool_info(self, tool_name: str = None) -> Dict:
        """Get information about registered tools"""
        if tool_name:
            return self.tools.get(tool_name, {})
        
        return {
            'total_tools': len(self.tools),
            'tools': {
                name: {
                    'description': info['description'],
                    'requires_approval': info['requires_approval'],
                    'call_count': info['call_count']
                }
                for name, info in self.tools.items()
            }
        }
    
    def get_execution_log(self, limit: int = 50) -> List[Dict]:
        """Get recent execution logs"""
        return self.execution_log[-limit:]
    
    def clear_log(self):
        """Clear execution log"""
        self.execution_log = []

# Global registry instance
tool_registry = ToolRegistry()

# Example mock tools (will be replaced with real implementations)
@tool_registry.register(description="Create a Jira ticket", requires_approval=True)
def create_jira_ticket(summary: str, description: str, project: str = "BA"):
    """Mock Jira ticket creation"""
    ticket_id = f"{project}-{hashlib.md5(summary.encode()).hexdigest()[:8]}"
    return {
        'ticket_id': ticket_id,
        'summary': summary,
        'project': project,
        'status': 'created',
        'url': f'https://jira.example.com/browse/{ticket_id}'
    }

@tool_registry.register(description="Execute SQL query (read-only)")
def execute_sql_query(query: str, database: str = "warehouse"):
    """Mock SQL query execution"""
    # Security check - block dangerous operations
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE']
    query_upper = query.upper()
    
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return {
                'error': f"Dangerous operation '{keyword}' not allowed",
                'query': query[:100]
            }
    
    return {
        'results': [
            {'id': 1, 'name': 'Sample Result 1'},
            {'id': 2, 'name': 'Sample Result 2'}
        ],
        'row_count': 2,
        'query': query[:100]
    }

@tool_registry.register(description="Send message to Slack")
def send_slack_message(channel: str, message: str, user_id: str = None):
    """Mock Slack message sending"""
    return {
        'success': True,
        'channel': channel,
        'message_preview': message[:100],
        'timestamp': datetime.now().isoformat()
    }

@tool_registry.register(description="Search Confluence pages")
def search_confluence(query: str, space: str = None, limit: int = 5):
    """Mock Confluence search"""
    return {
        'results': [
            {'title': f'Document about {query}', 'url': f'https://confluence/wiki/{i}'}
            for i in range(min(limit, 3))
        ],
        'query': query,
        'total': min(limit, 3)
    }

# Test the tool registry
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Tool Registry")
    print("=" * 60)
    
    # List all tools
    info = tool_registry.get_tool_info()
    print(f"\n📋 Registered Tools ({info['total_tools']}):")
    for name, details in info['tools'].items():
        print(f"  • {name}: {details['description'][:50]}...")
    
    # Execute a tool
    print("\n🔧 Executing create_jira_ticket...")
    result = tool_registry.execute(
        'create_jira_ticket',
        user_id='test_user',
        summary='Add login feature',
        description='Implement user authentication'
    )
    print(f"  Result: {result}")
    
    # Execute SQL query
    print("\n🔧 Executing execute_sql_query...")
    result = tool_registry.execute(
        'execute_sql_query',
        user_id='test_user',
        query='SELECT * FROM users LIMIT 10'
    )
    print(f"  Result: {result}")
    
    # Try dangerous SQL
    print("\n🔧 Testing dangerous SQL...")
    result = tool_registry.execute(
        'execute_sql_query',
        user_id='test_user',
        query='DROP TABLE users'
    )
    print(f"  Result: {result}")
    
    # Show execution log
    print("\n📜 Execution Log:")
    for log in tool_registry.get_execution_log(3):
        print(f"  • {log['tool']} - Success: {log.get('success', False)}")
    
    print("\n" + "=" * 60)
    print("✅ Tool Registry test complete!")
