"""
Base viewsets for tenant-aware API views.
"""
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from .models import current_tenant


class TenantAwareViewSet(viewsets.ModelViewSet):
    """
    Base viewset that automatically filters by tenant and sets tenant on create.
    """
    
    def get_queryset(self):
        """Filter queryset by current tenant."""
        queryset = super().get_queryset()
        if not self.request.tenant:
            return queryset.none()
        return queryset
    
    def perform_create(self, serializer):
        """Set tenant and created_by on object creation."""
        if not self.request.tenant:
            raise PermissionDenied("No tenant context available")
        
        serializer.save(
            tenant=self.request.tenant,
            created_by=self.request.user
        )