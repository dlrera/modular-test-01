"""
PM Template API views.
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.tenancy.views import TenantAwareViewSet
from core.auth.permissions import RoleBasedPermission
from .models import PMTemplate
from .serializers import PMTemplateSerializer
from .services import PMTemplateService


class PMTemplateViewSet(TenantAwareViewSet):
    """
    API viewset for PM template management.
    """
    queryset = PMTemplate.objects.all()
    serializer_class = PMTemplateSerializer
    permission_classes = [RoleBasedPermission]
    
    role_permissions = {
        'list': ['user', 'manager', 'admin'],
        'retrieve': ['user', 'manager', 'admin'],
        'create': ['manager', 'admin'],
        'update': ['manager', 'admin'],
        'partial_update': ['manager', 'admin'],
        'destroy': ['admin'],
        'generate_ai': ['manager', 'admin'],
    }
    
    @action(detail=False, methods=['post'])
    def generate_ai(self, request):
        """
        Generate PM template from AI prompt.
        """
        prompt = request.data.get('prompt', '')
        if not prompt:
            return Response(
                {'error': 'Prompt is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = PMTemplateService(request.user, request.tenant)
        template_dto = service.generate_from_ai(prompt)
        
        # Get created template for response
        template = PMTemplate.objects.get(id=template_dto.id)
        serializer = PMTemplateSerializer(template)
        
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )