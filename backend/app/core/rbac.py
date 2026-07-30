from typing import List, Dict, Set

# Enterprise Roles
ROLE_OWNER = "OWNER"
ROLE_TEMPLE_STAFF = "TEMPLE_STAFF"
ROLE_VOLUNTEER = "VOLUNTEER"
ROLE_FUTURE_ADMIN = "FUTURE_ADMIN"
ROLE_SUPER_ADMIN = "SUPER_ADMIN"

# Enterprise Permission Codes
PERM_VISITOR_REGISTER = "visitor:register"
PERM_VISITOR_VIEW = "visitor:view"
PERM_VISITOR_CHECKOUT = "visitor:checkout"
PERM_REPORTS_READ = "reports:read"
PERM_REPORTS_EXPORT = "reports:export"
PERM_BROADCAST_CREATE = "broadcast:create"
PERM_BROADCAST_VIEW = "broadcast:view"
PERM_SETTINGS_READ = "settings:read"
PERM_SETTINGS_MANAGE = "settings:manage"
PERM_AUDIT_READ = "audit:read"
PERM_ANALYTICS_READ = "analytics:read"

# Default Role-Permissions Matrix
ROLE_PERMISSIONS_MATRIX: Dict[str, Set[str]] = {
    ROLE_SUPER_ADMIN: {
        PERM_VISITOR_REGISTER, PERM_VISITOR_VIEW, PERM_VISITOR_CHECKOUT,
        PERM_REPORTS_READ, PERM_REPORTS_EXPORT, PERM_BROADCAST_CREATE,
        PERM_BROADCAST_VIEW, PERM_SETTINGS_READ, PERM_SETTINGS_MANAGE, PERM_AUDIT_READ, PERM_ANALYTICS_READ
    },
    ROLE_OWNER: {
        PERM_VISITOR_VIEW, PERM_REPORTS_READ, PERM_REPORTS_EXPORT,
        PERM_BROADCAST_CREATE, PERM_BROADCAST_VIEW, PERM_SETTINGS_READ,
        PERM_SETTINGS_MANAGE, PERM_AUDIT_READ, PERM_ANALYTICS_READ
    },
    ROLE_TEMPLE_STAFF: {
        PERM_VISITOR_REGISTER, PERM_VISITOR_VIEW, PERM_VISITOR_CHECKOUT,
        PERM_REPORTS_READ, PERM_REPORTS_EXPORT, PERM_BROADCAST_VIEW, PERM_SETTINGS_READ, PERM_ANALYTICS_READ
    },
    ROLE_VOLUNTEER: {
        PERM_VISITOR_REGISTER, PERM_VISITOR_VIEW, PERM_VISITOR_CHECKOUT
    },
    ROLE_FUTURE_ADMIN: {
        PERM_VISITOR_VIEW, PERM_REPORTS_READ, PERM_BROADCAST_VIEW, PERM_SETTINGS_READ
    },
}


def user_has_permission(user_roles: List[str], permission_code: str) -> bool:
    """Check if any of the user's assigned roles grant the specified permission."""
    if ROLE_SUPER_ADMIN in user_roles:
        return True
    
    for role in user_roles:
        granted_permissions = ROLE_PERMISSIONS_MATRIX.get(role, set())
        if permission_code in granted_permissions:
            return True
            
    return False
