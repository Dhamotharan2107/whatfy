# Advanced Feature Implementation Guide for MCP Server

## Quick Implementation Checklist

### Phase 1: Critical Features (Must Implement)

#### 1. Enhanced Rate Limiting with Tiers

**Files to Update:**
- `mcp_server.py` (update RateLimiter class)

**Implementation:**
```python
class TieredRateLimiter:
    """Multi-tier rate limiting system"""
    
    def __init__(self):
        self.tiers = {
            "free": {"daily": 1000, "per_minute": 10, "burst": 3},
            "premium": {"daily": 10000, "per_minute": 50, "burst": 5},
            "enterprise": {"daily": 100000, "per_minute": 500, "burst": 10}
        }
        self.user_requests = defaultdict(lambda: {"timestamps": [], "daily_count": 0})
        self.global_daily_count = 0
        self.lock = threading.Lock()
    
    async def check_rate_limit(self, user_id: str, tier: str = "free") -> dict:
        """Check rate limit for user with tier-based limits"""
        current_time = time.time()
        limits = self.tiers.get(tier, self.tiers["free"])
        
        with self.lock:
            # Check global daily limit
            if self.global_daily_count >= limits["daily"]:
                return {"allowed": False, "code": 429, "message": "Global daily limit exceeded"}
            
            # Check user daily limit
            user_data = self.user_requests[user_id]
            window_start = current_time - 86400  # 24 hours
            user_data["timestamps"] = [
                ts for ts in user_data["timestamps"] if ts > window_start
            ]
            if len(user_data["timestamps"]) >= limits["daily"]:
                return {"allowed": False, "code": 429, "message": "Daily limit exceeded"}
            
            # Check per-minute limit
            minute_start = current_time - 60
            minute_count = sum(
                1 for ts in user_data["timestamps"]
                if ts > minute_start
            )
            if minute_count >= limits["per_minute"]:
                return {"allowed": False, "code": 429, "message": "Minute limit exceeded"}
            
            # Record request
            user_data["timestamps"].append(current_time)
            self.global_daily_count += 1
            
            return {
                "allowed": True,
                "code": 200,
                "limit": limits["per_minute"],
                "window": 60,
                "current": minute_count + 1,
                "tier": tier
            }
    
    def get_user_stats(self, user_id: str) -> dict:
        """Get user rate limit statistics"""
        with self.lock:
            user_data = self.user_requests[user_id]
            return {
                "daily_used": len(user_data["timestamps"]),
                "daily_limit": self.tiers["free"]["daily"],
                "daily_remaining": self.tiers["free"]["daily"] - len(user_data["timestamps"]),
                "per_minute_used": 0,  # Would calculate properly
                "last_reset": "24 hours ago"
            }
```

**Add to MCP Server:**
```python
# Replace existing RateLimiter with TieredRateLimiter
tiered_rate_limiter = TieredRateLimiter()

# Update endpoint
@app.post("/api/messages/send")
async def send_messages(
    user_id: str,
    batch_id: str,
    message_template: str = "Hi",
    dry_run: bool = False,
    tier: str = "free"  # Add tier parameter
):
    # Check tier-based rate limit
    rate_limit = await tiered_rate_limiter.check_rate_limit(user_id, tier)
    
    if not rate_limit["allowed"]:
        raise HTTPException(
            status_code=rate_limit["code"],
            detail=rate_limit["message"]
        )
    
    # Continue with message sending...
```

---

#### 2. Audit Logging System

**New File: `audit_logger.py`**
```python
import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

@dataclass
class AuditLog:
    id: int
    timestamp: int
    user_id: str
    api_key: Optional[str]
    endpoint: str
    method: str
    request_data: dict
    response_code: int
    response_time: int
    ip_address: str
    user_agent: str
    error_message: Optional[str] = None
    success: bool = True

class AuditLogger:
    """Comprehensive audit logging system"""
    
    def __init__(self, log_file: str = "audit.log"):
        self.log_file = log_file
        self.logger = self._setup_logger()
        self.log_count = 0
    
    def _setup_logger(self):
        """Configure audit logger"""
        logger = logging.getLogger("audit_logger")
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        return logger
    
    def log_request(
        self,
        user_id: str,
        endpoint: str,
        method: str,
        request_data: dict,
        response_code: int,
        response_time: int,
        ip_address: str = "127.0.0.1",
        user_agent: str = "unknown",
        api_key: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Log API request"""
        try:
            log_entry = {
                "timestamp": int(time.time()),
                "user_id": user_id,
                "api_key": api_key,
                "endpoint": endpoint,
                "method": method,
                "request_data": request_data,
                "response_code": response_code,
                "response_time": response_time,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "error_message": error_message,
                "success": response_code < 400
            }
            
            # Log to file
            self.logger.info(json.dumps(log_entry))
            
            # Log to console
            print(f"[AUDIT] {method} {endpoint} - {response_code} ({response_time}ms)")
            
            self.log_count += 1
            
            # Limit log file size
            if self.log_count > 10000:
                self._rotate_logs()
                
        except Exception as e:
            print(f"[AUDIT ERROR] Failed to log: {e}")
    
    def _rotate_logs(self):
        """Rotate log files to prevent size issues"""
        try:
            os.rename(self.log_file, f"{self.log_file}.{int(time.time())}")
        except Exception:
            pass
    
    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> list:
        """Get audit logs with filters"""
        logs = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    try:
                        log_entry = json.loads(line)
                        
                        # Apply filters
                        if user_id and log_entry.get("user_id") != user_id:
                            continue
                        if start_time and log_entry.get("timestamp") < start_time:
                            continue
                        if end_time and log_entry.get("timestamp") > end_time:
                            continue
                        
                        logs.append(log_entry)
                        
                        if len(logs) >= limit:
                            break
                            
                    except json.JSONDecodeError:
                        continue
                        
        except FileNotFoundError:
            pass
            
        return logs[-limit:]
    
    def get_statistics(self) -> dict:
        """Get audit statistics"""
        logs = self.get_audit_logs()
        
        if not logs:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "avg_response_time": 0,
                "endpoints": {}
            }
        
        successful = sum(1 for log in logs if log.get("success", False))
        failed = len(logs) - successful
        
        response_times = [
            log.get("response_time", 0) for log in logs
        ]
        avg_time = sum(response_times) / len(response_times) if response_times else 0
        
        endpoints = {}
        for log in logs:
            endpoint = log.get("endpoint", "unknown")
            endpoints[endpoint] = endpoints.get(endpoint, 0) + 1
        
        return {
            "total_requests": len(logs),
            "successful_requests": successful,
            "failed_requests": failed,
            "failed_rate": (failed / len(logs) * 100) if logs else 0,
            "avg_response_time": avg_time,
            "endpoints": dict(sorted(endpoints.items(), key=lambda x: x[1], reverse=True)[:10])
        }
```

**Add to MCP Server:**
```python
# Initialize audit logger
audit_logger = AuditLogger()

# Wrap all endpoints with audit logging
@app.post("/api/messages/send")
async def send_messages(...):
    start_time = time.time()
    
    # Add audit logging to all endpoints
    audit_logger.log_request(
        user_id=user_id,
        endpoint="/api/messages/send",
        method="POST",
        request_data={"batch_id": batch_id, "template": message_template},
        response_code=200,
        response_time=int(time.time() - start_time),
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown")
    )
    
    # ... rest of the code
```

---

#### 3. Groups API

**New File: `groups_api.py`**
```python
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import uuid

groups_router = APIRouter(prefix="/api/groups", tags=["Groups"])

# Request Models
class GroupCreateRequest(BaseModel):
    group_name: str
    participants: List[str]
    message_template: Optional[str] = "Welcome to the group!"

class GroupMessageRequest(BaseModel):
    group_id: str
    message: str

@groups_router.post("/create")
async def create_group(user_id: str, request: GroupCreateRequest):
    """Create a new WhatsApp group"""
    try:
        # Validate user permissions
        if not has_permission(user_id, "create_group"):
            raise HTTPException(status_code=403, detail="Permission denied")
        
        # Generate group ID
        group_id = f"group_{uuid.uuid4()}"
        
        # Create group via WhatsApp API
        group_data = await whatsapp_api.create_group(
            name=request.group_name,
            participants=request.participants
        )
        
        # Send welcome message to all participants
        message_results = []
        for participant in request.participants[:100]:  # Limit for safety
            result = await whatsapp_api.send_message(
                to=participant,
                text=request.message_template
            )
            message_results.append({
                "phone": participant,
                "status": "sent" if result else "failed",
                "message_id": result.get("message_id") if result else None
            })
        
        # Save to database
        db.execute("""
            INSERT INTO groups (
                id, user_id, name, created_at, member_count
            ) VALUES (?, ?, ?, ?, ?)
        """, (group_id, user_id, request.group_name, int(time.time()), len(request.participants)))
        
        return {
            "success": True,
            "group_id": group_id,
            "group_name": request.group_name,
            "members": message_results,
            "message": f"Group created with {len(request.participants)} members"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create group: {str(e)}")

@groups_router.get("/{group_id}")
async def get_group_details(group_id: str, user_id: str):
    """Get group details and members"""
    # Check ownership or access
    group = db.execute(
        "SELECT * FROM groups WHERE id = ? AND user_id = ?",
        (group_id, user_id)
    ).fetchone()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get group members
    members = db.execute(
        "SELECT * FROM group_members WHERE group_id = ?",
        (group_id,)
    ).fetchall()
    
    return {
        "group_id": group_id,
        "name": group["name"],
        "members_count": len(members),
        "members": members,
        "created_at": group["created_at"]
    }

@groups_router.post("/{group_id}/message")
async def send_group_message(group_id: str, user_id: str, request: GroupMessageRequest):
    """Send message to entire group"""
    # Check ownership
    group = db.execute(
        "SELECT * FROM groups WHERE id = ? AND user_id = ?",
        (group_id, user_id)
    ).fetchone()
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Get all members
    members = db.execute(
        "SELECT phone FROM group_members WHERE group_id = ?",
        (group_id,)
    ).fetchall()
    
    # Send message to each member
    results = []
    for member in members:
        result = await whatsapp_api.send_message(
            to=member["phone"],
            text=request.message
        )
        results.append({
            "phone": member["phone"],
            "status": "sent" if result else "failed",
            "message_id": result.get("message_id") if result else None
        })
    
    return {
        "success": True,
        "group_id": group_id,
        "total_recipients": len(members),
        "sent": len([r for r in results if r["status"] == "sent"]),
        "results": results[:100]  # Limit for response size
    }
```

**Integrate with MCP Server:**
```python
# In mcp_server.py
from groups_api import groups_router

# Include the router
app.include_router(groups_router)
```

---

## Quick Start Implementation Commands

```bash
# 1. Install additional dependencies
pip install python-jose[cryptography] passlib[bcrypt] redis

# 2. Start MCP server
python mcp_server.py

# 3. Test the enhanced rate limiting
curl "http://localhost:8001/api/rate-limit/check?user_id=test_user"

# 4. Test audit logging
curl -X POST "http://localhost:8001/api/messages/send?user_id=test_user" \
  -d "batch_id=uuid-here" \
  -d "message_template=Test message"

# 5. Check audit logs
python -c "from audit_logger import AuditLogger; logger = AuditLogger(); print(logger.get_statistics())"
```

---

## Implementation Timeline

**Day 1: Rate Limiting Enhancement**
- Implement TieredRateLimiter class
- Update existing endpoints to use tier-based limits
- Add user tier management

**Day 2: Audit Logging**
- Create AuditLogger class
- Add audit logging to all endpoints
- Create audit log retrieval endpoint

**Day 3: Groups API**
- Create groups_api.py file
- Implement group creation and management
- Add group messaging functionality

**Day 4: Testing**
- Test rate limiting with multiple users
- Verify audit logs are being captured
- Test group creation and messaging
- Load testing with 1000+ users

---

## Performance Considerations

1. **Rate Limiting Performance:**
   - Use thread locks for concurrent access
   - Consider Redis for distributed rate limiting
   - Implement sliding window for accurate counting

2. **Audit Log Performance:**
   - Write logs asynchronously
   - Use batch writing for large volumes
   - Implement log rotation and archival

3. **Groups API Performance:**
   - Use async/await for non-blocking operations
   - Implement message batching
   - Add caching for group metadata

---

## Security Considerations

1. **Rate Limiting:**
   - Implement global rate limits
   - Add exponential backoff for 429 errors
   - Protect against rate limit bypass

2. **Audit Logging:**
   - Sanitize sensitive data in logs
   - Implement log file permissions
   - Regular security audits of logs

3. **Groups API:**
   - Validate group membership
   - Prevent spam (max 1000 messages per request)
   - Rate limit group operations

---

## Success Metrics

1. **Rate Limiting:**
   - Successfully block 99% of rate limit violations
   - Response time under 10ms for rate limit checks

2. **Audit Logging:**
   - 100% request coverage
   - Log file retention > 90 days
   - Search efficiency < 100ms

3. **Groups API:**
   - Group creation time < 2 seconds
   - Message sending success rate > 95%
   - Handle 1000+ members per group

---

This implementation guide provides a complete roadmap for adding the critical advanced features from OpenWA to your MCP server. Start with Phase 1 features and build incrementally for best results.
