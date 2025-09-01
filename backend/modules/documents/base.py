"""
Temporary base viewset for development testing.
"""
from rest_framework import viewsets


class SimplifiedTenantViewSet(viewsets.ModelViewSet):
    """
    Simplified viewset for testing without tenant requirements.
    """
    
    def get_queryset(self):
        """Return all objects for now."""
        return super().get_queryset()
    
    def perform_create(self, serializer):
        """Save without tenant for testing."""
        # Get the first tenant or create a default one
        from core.tenancy.models import Account
        
        tenant = Account.objects.first()
        if not tenant:
            tenant = Account.objects.create(
                name="Test Company",
                subdomain="test",
                is_active=True
            )
        
        serializer.save(tenant=tenant)