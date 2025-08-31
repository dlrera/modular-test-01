"""
Document API views.
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.tenancy.views import TenantAwareViewSet
from core.auth.permissions import RoleBasedPermission
from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer
from .services import DocumentService, DocumentCreateDTO


class DocumentViewSet(TenantAwareViewSet):
    """
    API viewset for document management.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [RoleBasedPermission]
    
    # Define role-based permissions for actions
    role_permissions = {
        'list': ['user', 'manager', 'admin'],
        'retrieve': ['user', 'manager', 'admin'],
        'create': ['user', 'manager', 'admin'],
        'update': ['manager', 'admin'],
        'partial_update': ['manager', 'admin'],
        'destroy': ['admin'],
        'upload': ['user', 'manager', 'admin'],
        'archive': ['manager', 'admin'],
    }
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Upload a new document.
        """
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Use service layer for business logic
        service = DocumentService(request.user, request.tenant)
        dto = DocumentCreateDTO(
            title=serializer.validated_data['title'],
            file=serializer.validated_data['file'],
            description=serializer.validated_data.get('description', ''),
            tags=serializer.validated_data.get('tags', [])
        )
        
        document_dto = service.create_document(dto)
        
        # Get the created document for response
        document = Document.objects.get(id=document_dto.id)
        response_serializer = DocumentSerializer(document)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archive a document.
        """
        service = DocumentService(request.user, request.tenant)
        
        if service.archive_document(pk):
            return Response({'status': 'archived'})
        else:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )