"""
Role-based permission classes for API views.
"""
from rest_framework import permissions
from core.tenancy.models import UserProfile


class IsTenantUser(permissions.BasePermission):
    """
    Base permission class ensuring user belongs to a tenant.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Check if user has a profile with an active account
        try:
            profile = request.user.profile
            return profile.is_active and profile.account.is_active
        except UserProfile.DoesNotExist:
            return False


class IsAdminUser(IsTenantUser):
    """
    Permission class for admin-only operations.
    """
    def has_permission(self, request, view):
        has_tenant = super().has_permission(request, view)
        if not has_tenant:
            return False
        
        return request.user.profile.role == 'admin'


class IsManagerOrAdmin(IsTenantUser):
    """
    Permission class for manager and admin operations.
    """
    def has_permission(self, request, view):
        has_tenant = super().has_permission(request, view)
        if not has_tenant:
            return False
        
        return request.user.profile.role in ['manager', 'admin']


class RoleBasedPermission(IsTenantUser):
    """
    Flexible role-based permission class.
    Views can define role_permissions dict to specify required roles per action.
    
    Example:
        role_permissions = {
            'list': ['user', 'manager', 'admin'],
            'create': ['manager', 'admin'],
            'destroy': ['admin']
        }
    """
    def has_permission(self, request, view):
        has_tenant = super().has_permission(request, view)
        if not has_tenant:
            return False
        
        # Get role requirements for this action
        action = view.action if hasattr(view, 'action') else None
        if not action:
            # For non-viewset views, map HTTP methods to actions
            method_map = {
                'GET': 'list',
                'POST': 'create',
                'PUT': 'update',
                'PATCH': 'partial_update',
                'DELETE': 'destroy'
            }
            action = method_map.get(request.method, 'list')
        
        # Check if view defines role permissions
        if hasattr(view, 'role_permissions'):
            allowed_roles = view.role_permissions.get(action, [])
            return request.user.profile.role in allowed_roles
        
        # Default: allow all authenticated tenant users
        return True