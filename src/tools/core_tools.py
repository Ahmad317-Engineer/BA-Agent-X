"""
Core Tools - Jira, SQL, Slack, Confluence integrations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import hashlib
from pathlib import Path

# Mock implementations for development
# Replace with real API calls when credentials are available

class JiraTool:
    """Jira integration tool"""
    
    def __init__(self, url: str = None, email: str = None, token: str = None):
        self.url = url
        self.email = email
        self.token = token
        self.mode = "mock" if not all([url, email, token]) else "real"
        print(f"✅ JiraTool initialized ({self.mode} mode)")
    
    def create_ticket(self, project: str, summary: str, description: str, 
                      issue_type: str = "Task", priority: str = "Medium") -> Dict:
        """Create a Jira ticket"""
        ticket_id = f"{project.upper()}-{hashlib.md5(summary.encode()).hexdigest()[:6].upper()}"
        
        return {
            'ticket_id': ticket_id,
            'summary': summary,
            'description': description[:200],
            'project': project,
            'issue_type': issue_type,
            'priority': priority,
            'status': 'Open',
            'url': f"{self.url or 'https://mock-jira'}/browse/{ticket_id}",
            'created_at': datetime.now().isoformat()
        }
    
    def search_tickets(self, project: str = None, assignee: str = None, 
                       status: str = None, limit: int = 10) -> List[Dict]:
        """Search Jira tickets"""
        # Mock results
        tickets = []
        for i in range(min(limit, 5)):
            tickets.append({
                'ticket_id': f"{project or 'BA'}-{i+1:04d}",
                'summary': f"Sample ticket {i+1}",
                'status': status or 'Open',
                'assignee': assignee or 'unassigned',
                'created': datetime.now().isoformat()
            })
        return tickets

class SQLTool:
    """SQL query tool with security validation"""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string
        self.mode = "mock" if not connection_string else "real"
        print(f"✅ SQLTool initialized ({self.mode} mode)")
    
    def validate_query(self, query: str) -> tuple:
        """Validate query is read-only"""
        query_upper = query.upper().strip()
        
        # Block dangerous operations
        dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 
                     'CREATE', 'TRUNCATE', 'MERGE', 'REPLACE']
        
        for keyword in dangerous:
            if keyword in query_upper:
                return False, f"Dangerous operation '{keyword}' not allowed"
        
        # Allow SELECT, WITH, SHOW, DESCRIBE
        allowed = ['SELECT', 'WITH', 'SHOW', 'DESCRIBE', 'EXPLAIN']
        if not any(query_upper.startswith(word) for word in allowed):
            return False, "Only SELECT queries are allowed"
        
        return True, "OK"
    
    def execute_query(self, query: str, database: str = "default", limit: int = 100) -> Dict:
        """Execute a read-only SQL query"""
        # Validate
        is_valid, message = self.validate_query(query)
        if not is_valid:
            return {'error': message, 'query': query[:100]}
        
        # Mock results
        if self.mode == "mock":
            return {
                'success': True,
                'results': [
                    {'id': i, 'name': f'Result {i}', 'created_at': datetime.now().isoformat()}
                    for i in range(1, min(limit, 6))
                ],
                'row_count': min(limit, 5),
                'query': query[:100],
                'database': database
            }
        else:
            # Real implementation would go here
            return {'error': 'Real SQL execution not implemented in mock mode'}

class SlackTool:
    """Slack integration tool"""
    
    def __init__(self, bot_token: str = None, app_token: str = None):
        self.bot_token = bot_token
        self.app_token = app_token
        self.mode = "mock" if not bot_token else "real"
        print(f"✅ SlackTool initialized ({self.mode} mode)")
    
    def send_message(self, channel: str, message: str, thread_ts: str = None) -> Dict:
        """Send message to Slack channel"""
        return {
            'success': True,
            'channel': channel,
            'message_preview': message[:100],
            'thread_ts': thread_ts or datetime.now().timestamp(),
            'timestamp': datetime.now().isoformat(),
            'mode': self.mode
        }
    
    def get_channel_history(self, channel: str, limit: int = 10) -> List[Dict]:
        """Get channel message history"""
        return [
            {
                'user': f'user_{i}',
                'text': f'Mock message {i}',
                'timestamp': datetime.now().isoformat(),
                'channel': channel
            }
            for i in range(min(limit, 5))
        ]

class ConfluenceTool:
    """Confluence integration tool"""
    
    def __init__(self, url: str = None, username: str = None, token: str = None):
        self.url = url
        self.username = username
        self.token = token
        self.mode = "mock" if not all([url, username, token]) else "real"
        print(f"✅ ConfluenceTool initialized ({self.mode} mode)")
    
    def search_pages(self, query: str, space: str = None, limit: int = 10) -> List[Dict]:
        """Search Confluence pages"""
        return [
            {
                'title': f'Page about {query} - {i}',
                'url': f"{self.url or 'https://mock-confluence'}/wiki/spaces/{space or 'BA'}/page/{i}",
                'space': space or 'BA',
                'excerpt': f'This page contains information about {query}...',
                'last_modified': datetime.now().isoformat()
            }
            for i in range(1, min(limit, 4))
        ]
    
    def get_page_content(self, page_id: str) -> Dict:
        """Get page content by ID"""
        return {
            'page_id': page_id,
            'title': f'Page {page_id}',
            'content': f'This is the content of page {page_id}',
            'url': f"{self.url or 'https://mock-confluence'}/wiki/spaces/BA/pages/{page_id}",
            'version': 1,
            'last_modified': datetime.now().isoformat()
        }
    
    def create_page(self, space: str, title: str, content: str, parent_id: str = None) -> Dict:
        """Create a new Confluence page"""
        page_id = hashlib.md5(f"{space}{title}".encode()).hexdigest()[:8]
        return {
            'page_id': page_id,
            'title': title,
            'space': space,
            'url': f"{self.url or 'https://mock-confluence'}/wiki/spaces/{space}/pages/{page_id}",
            'created_at': datetime.now().isoformat(),
            'content_preview': content[:100]
        }

# Test the tools
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Core Tools")
    print("=" * 60)
    
    # Test Jira
    print("\n📋 Testing JiraTool...")
    jira = JiraTool()
    ticket = jira.create_ticket("BA", "Add authentication", "Implement login feature")
    print(f"  Created ticket: {ticket['ticket_id']}")
    
    # Test SQL
    print("\n🗄️ Testing SQLTool...")
    sql = SQLTool()
    result = sql.execute_query("SELECT * FROM users LIMIT 5")
    print(f"  Query result: {result['row_count']} rows")
    
    # Test dangerous SQL
    print("\n🔒 Testing SQL security...")
    result = sql.execute_query("DROP TABLE users")
    print(f"  Security block: {result.get('error', 'OK')}")
    
    # Test Slack
    print("\n💬 Testing SlackTool...")
    slack = SlackTool()
    msg = slack.send_message("#general", "Hello from BA Agent!")
    print(f"  Message sent to {msg['channel']}")
    
    # Test Confluence
    print("\n📚 Testing ConfluenceTool...")
    confluence = ConfluenceTool()
    pages = confluence.search_pages("API documentation")
    print(f"  Found {len(pages)} pages")
    
    print("\n" + "=" * 60)
    print("✅ Core Tools test complete!")
