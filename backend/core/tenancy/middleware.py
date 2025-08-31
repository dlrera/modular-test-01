"""
Middleware for handling tenant context in requests.
"""
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import get_object_or_404
from .models import current_tenant, UserProfile


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware that sets the current tenant context based on authenticated user.
    """
    def process_request(self, request):
        """Set tenant context from authenticated user's account."""
        if request.user.is_authenticated:
            try:
                # Get user's profile and set their account as current tenant
                profile = UserProfile.objects.select_related('account').get(
                    user=request.user
                )
                current_tenant.set(profile.account)
                request.tenant = profile.account
                request.user_role = profile.role
            except UserProfile.DoesNotExist:
                # User has no profile/account association
                current_tenant.set(None)
                request.tenant = None
                request.user_role = None
        else:
            current_tenant.set(None)
            request.tenant = None
            request.user_role = None
    
    def process_response(self, request, response):
        """Clear tenant context after request processing."""
        current_tenant.set(None)
        return response