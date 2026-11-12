"""
Role-Based Access Control (RBAC) & Tenant Isolation for MerchantOS Agents.
Enforces tenant isolation and strict role permissions mapped to JWT backend roles:
- OWNER / ADMIN -> Role.OWNER
- SUPERVISOR / MANAGER -> Role.SUPERVISOR
- STAFF -> Role.STAFF
"""
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, Optional


class Role(str, Enum):
    OWNER = "OWNER"
    SUPERVISOR = "SUPERVISOR"
    STAFF = "STAFF"


class UnauthorizedAgentActionError(Exception):
    """Raised when an agent attempts a tool execution exceeding caller RBAC privileges."""
    pass


class TenantIsolationError(Exception):
    """Raised when a request lacks a valid tenant/business identifier."""
    pass


def normalize_role(raw_role: Any) -> Role:
    """Normalizes backend JWT roles (owner, admin, manager, staff) to Agent Role enum."""
    if isinstance(raw_role, Role):
        return raw_role
    val = str(raw_role or "STAFF").strip().upper()
    if val in ("OWNER", "ADMIN"):
        return Role.OWNER
    if val in ("SUPERVISOR", "MANAGER"):
        return Role.SUPERVISOR
    return Role.STAFF


def require_agent_role(*allowed_roles: Role):
    """Decorator enforcing strict role-based permission & tenant isolation on agent tools."""
    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args, **kwargs):
            context: Optional[Dict[str, Any]] = kwargs.get("context")
            if not context:
                for arg in args:
                    if isinstance(arg, dict) and ("role" in arg or "tenant_id" in arg):
                        context = arg
                        break

            if not context:
                raise TenantIsolationError(f"Action '{func.__name__}' denied: Missing execution context.")

            tenant_id = context.get("tenant_id") or context.get("business_id")
            if not tenant_id:
                raise TenantIsolationError(f"Action '{func.__name__}' denied: Missing valid tenant_id context.")

            caller_role = normalize_role(context.get("role"))
            if caller_role not in allowed_roles:
                raise UnauthorizedAgentActionError(
                    f"Access Denied: Role '{caller_role.value}' is not authorized to execute '{func.__name__}'. "
                    f"Required roles: {[r.value for r in allowed_roles]}."
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator
