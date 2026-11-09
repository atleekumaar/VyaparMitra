"""
MerchantOS RBAC & Security Enforcers for Agent Tool Calling.
Enforces tenant isolation and strict 3-role permissions: OWNER, SUPERVISOR, STAFF.
"""
from enum import Enum
from functools import wraps
from typing import Callable, Any, Dict

class Role(str, Enum):
    OWNER = "OWNER"
    SUPERVISOR = "SUPERVISOR"
    STAFF = "STAFF"

class UnauthorizedAgentActionError(Exception):
    """Raised when an agent tool is invoked outside permitted role context."""
    pass

class TenantIsolationError(Exception):
    """Raised when a request lacks a valid tenant identifier."""
    pass

def require_agent_role(*allowed_roles: Role):
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            context: Dict[str, Any] = kwargs.get("context") or {}
            
            tenant_id = context.get("tenant_id")
            if not tenant_id:
                raise TenantIsolationError(f"Action '{func.__name__}' denied: Missing valid tenant_id context.")
                
            user_role = context.get("role", Role.STAFF.value)
            allowed_role_values = [r.value for r in allowed_roles]
            
            if user_role not in allowed_role_values:
                raise UnauthorizedAgentActionError(
                    f"Action '{func.__name__}' is restricted. Required: {allowed_role_values}, Invoked by: {user_role}"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
