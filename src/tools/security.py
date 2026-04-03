"""
Tool Security - Validation, rate limiting, audit logging
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path

class RateLimiter:
    """Rate limiting for tool usage"""
    
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window  # seconds
        self.calls: Dict[str, List[datetime]] = defaultdict(list)
    
    def check_limit(self, user_id: str, tool_name: str) -> tuple:
        """Check if user has exceeded rate limit"""
        key = f"{user_id}:{tool_name}"
        now = datetime.now()
        
        # Clean old calls
        self.calls[key] = [
            call_time for call_time in self.calls[key]
            if now - call_time < timedelta(seconds=self.time_window)
        ]
        
        # Check limit
        if len(self.calls[key]) >= self.max_calls:
            return False, f"Rate limit exceeded. Max {self.max_calls} calls per {self.time_window} seconds"
        
        # Record call
        self.calls[key].append(now)
        return True, "OK"

class AuditLogger:
    """Audit logging for tool executions"""
    
    def __init__(self, log_file: str = "./logs/audit.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.logs = self._load_logs()
    
    def _load_logs(self) -> List[Dict]:
        """Load existing logs"""
        if self.log_file.exists():
            with open(self.log_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_logs(self):
        """Save logs to disk"""
        with open(self.log_file, 'w') as f:
            json.dump(self.logs[-1000:], f, indent=2, default=str)
    
    def log(self, entry: Dict):
        """Log an audit entry"""
        entry['logged_at'] = datetime.now().isoformat()
        self.logs.append(entry)
        self._save_logs()
    
    def get_logs(self, user_id: str = None, tool_name: str = None, 
                 limit: int = 100) -> List[Dict]:
        """Get filtered logs"""
        results = self.logs[-limit:]
        
        if user_id:
            results = [l for l in results if l.get('user_id') == user_id]
        if tool_name:
            results = [l for l in results if l.get('tool_name') == tool_name]
        
        return results

class ApprovalGate:
    """Approval gate for sensitive operations"""
    
    def __init__(self):
        self.pending_approvals: Dict[str, Dict] = {}
        self.approved: Dict[str, Dict] = {}
    
    def request_approval(self, request_id: str, user_id: str, tool_name: str, 
                         params: Dict, reason: str) -> str:
        """Request approval for an operation"""
        self.pending_approvals[request_id] = {
            'request_id': request_id,
            'user_id': user_id,
            'tool_name': tool_name,
            'params': params,
            'reason': reason,
            'status': 'pending',
            'requested_at': datetime.now().isoformat()
        }
        return request_id
    
    def approve(self, request_id: str, approver_id: str) -> bool:
        """Approve a pending request"""
        if request_id in self.pending_approvals:
            request = self.pending_approvals[request_id]
            request['status'] = 'approved'
            request['approved_by'] = approver_id
            request['approved_at'] = datetime.now().isoformat()
            self.approved[request_id] = request
            del self.pending_approvals[request_id]
            return True
        return False
    
    def reject(self, request_id: str, approver_id: str, reason: str) -> bool:
        """Reject a pending request"""
        if request_id in self.pending_approvals:
            request = self.pending_approvals[request_id]
            request['status'] = 'rejected'
            request['rejected_by'] = approver_id
            request['rejection_reason'] = reason
            request['rejected_at'] = datetime.now().isoformat()
            del self.pending_approvals[request_id]
            return True
        return False
    
    def get_pending(self) -> List[Dict]:
        """Get all pending approvals"""
        return list(self.pending_approvals.values())
    
    def is_approved(self, request_id: str) -> bool:
        """Check if request is approved"""
        return request_id in self.approved

class SecurityManager:
    """Main security manager coordinating all security features"""
    
    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.audit_logger = AuditLogger()
        self.approval_gate = ApprovalGate()
    
    def validate_tool_call(self, user_id: str, tool_name: str, 
                           params: Dict, requires_approval: bool = False) -> Dict:
        """Validate a tool call before execution"""
        
        # Check rate limits
        allowed, message = self.rate_limiter.check_limit(user_id, tool_name)
        if not allowed:
            self.audit_logger.log({
                'user_id': user_id,
                'tool_name': tool_name,
                'action': 'blocked_rate_limit',
                'message': message
            })
            return {'allowed': False, 'reason': message}
        
        # Check if approval required
        if requires_approval:
            # Generate request ID
            import hashlib
            request_id = hashlib.md5(f"{user_id}{tool_name}{datetime.now()}".encode()).hexdigest()[:8]
            
            self.approval_gate.request_approval(
                request_id, user_id, tool_name, params,
                reason=f"Approval required for {tool_name}"
            )
            
            self.audit_logger.log({
                'user_id': user_id,
                'tool_name': tool_name,
                'action': 'pending_approval',
                'request_id': request_id
            })
            
            return {
                'allowed': False, 
                'requires_approval': True,
                'request_id': request_id,
                'reason': f"Approval required for {tool_name}"
            }
        
        # All checks passed
        self.audit_logger.log({
            'user_id': user_id,
            'tool_name': tool_name,
            'action': 'allowed',
            'params': {k: str(v)[:100] for k, v in params.items()}
        })
        
        return {'allowed': True}
    
    def log_execution(self, user_id: str, tool_name: str, 
                      success: bool, result: Any = None, error: str = None):
        """Log tool execution result"""
        self.audit_logger.log({
            'user_id': user_id,
            'tool_name': tool_name,
            'action': 'executed',
            'success': success,
            'result': str(result)[:200] if result else None,
            'error': error
        })

# Test security features
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Tool Security")
    print("=" * 60)
    
    security = SecurityManager()
    
    # Test rate limiting
    print("\n🔒 Testing Rate Limiting...")
    for i in range(12):
        result = security.validate_tool_call("user1", "test_tool", {})
        if i == 10:
            print(f"  Attempt {i+1}: {result.get('reason', 'Allowed')}")
    
    # Test approval gate
    print("\n✅ Testing Approval Gate...")
    result = security.validate_tool_call("user2", "dangerous_tool", {}, requires_approval=True)
    print(f"  Result: {result}")
    
    if result.get('requires_approval'):
        request_id = result['request_id']
        print(f"  Request ID: {request_id}")
        
        # Approve
        security.approval_gate.approve(request_id, "admin")
        print(f"  Approved!")
        
        # Check if approved
        is_approved = security.approval_gate.is_approved(request_id)
        print(f"  Is approved: {is_approved}")
    
    # Show audit logs
    print("\n📜 Audit Logs:")
    logs = security.audit_logger.get_logs(limit=5)
    for log in logs:
        print(f"  • {log.get('tool_name', 'unknown')} - {log.get('action')}")
    
    print("\n" + "=" * 60)
    print("✅ Security features test complete!")
