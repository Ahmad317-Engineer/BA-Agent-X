"""
Phase 3 Test Suite - Tool Integration
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_tool_registry():
    print("\n🔧 Testing Tool Registry...")
    from src.tools.registry import tool_registry
    
    # List tools
    info = tool_registry.get_tool_info()
    assert info['total_tools'] > 0
    print(f"  ✅ {info['total_tools']} tools registered")
    
    # Execute a tool
    result = tool_registry.execute('create_jira_ticket', 'test_user', 
                                   summary='Test', description='Test desc')
    assert result['success']
    print(f"  ✅ Tool execution successful")
    
    return True

def test_core_tools():
    print("\n🛠️ Testing Core Tools...")
    from src.tools.core_tools import JiraTool, SQLTool, SlackTool, ConfluenceTool
    
    # Jira
    jira = JiraTool()
    ticket = jira.create_ticket('TEST', 'Test', 'Desc')
    assert 'ticket_id' in ticket
    print(f"  ✅ Jira tool working")
    
    # SQL with security
    sql = SQLTool()
    result = sql.execute_query('SELECT * FROM users')
    assert result['success']
    print(f"  ✅ SQL tool working")
    
    # Test dangerous SQL blocked
    result = sql.execute_query('DROP TABLE users')
    assert 'error' in result
    print(f"  ✅ SQL security working")
    
    # Slack
    slack = SlackTool()
    msg = slack.send_message('#test', 'Hello')
    assert msg['success']
    print(f"  ✅ Slack tool working")
    
    # Confluence
    conf = ConfluenceTool()
    pages = conf.search_pages('test')
    assert len(pages) > 0
    print(f"  ✅ Confluence tool working")
    
    return True

def test_security():
    print("\n🔒 Testing Security...")
    from src.tools.security import SecurityManager, RateLimiter, AuditLogger
    
    security = SecurityManager()
    
    # Test rate limiting
    for i in range(5):
        result = security.validate_tool_call('user1', 'test', {})
    assert result['allowed']
    print(f"  ✅ Rate limiting working")
    
    # Test approval gate
    result = security.validate_tool_call('user2', 'danger', {}, requires_approval=True)
    assert result.get('requires_approval')
    print(f"  ✅ Approval gate working")
    
    # Test audit logging
    security.log_execution('user1', 'test_tool', True)
    logs = security.audit_logger.get_logs(limit=1)
    assert len(logs) > 0
    print(f"  ✅ Audit logging working")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 3 - TOOL INTEGRATION TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Tool Registry", test_tool_registry),
        ("Core Tools", test_core_tools),
        ("Security", test_security)
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
        print("✅ PHASE 3 COMPLETE! Ready for Phase 4 (Agent Nodes).")
    else:
        print("⚠️ Some tests failed. Review errors above.")
    print("=" * 60)
