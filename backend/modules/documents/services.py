"""
Document service layer implementing business logic.
"""
from dataclasses import dataclass
from typing import List, Optional
import uuid
from datetime import datetime
from django.core.files.uploadedfile import UploadedFile
from .models import Document


@dataclass
class DocumentCreateDTO:
    """Data transfer object for document creation."""
    title: str
    file: UploadedFile
    description: str = ""
    tags: List[str] = None
    metadata: dict = None


@dataclass
class DocumentDTO:
    """Data transfer object for document data."""
    id: int
    title: str
    file_name: str
    file_size: int
    mime_type: str
    created_at: datetime
    tags: List[str]


class DocumentService:
    """
    Service class for document operations.
    """
    
    def __init__(self, user, tenant):
        self.user = user
        self.tenant = tenant
    
    def create_document(self, dto: DocumentCreateDTO) -> DocumentDTO:
        """
        Create a new document.
        """
        # Generate S3 key with tenant isolation
        file_extension = dto.file.name.split('.')[-1] if '.' in dto.file.name else ''
        s3_key = self._generate_s3_key(dto.file.name, file_extension)
        
        # TODO: Upload file to S3
        # For now, we'll just save the path
        
        # Create document record
        document = Document.objects.create(
            tenant=self.tenant,
            created_by=self.user,
            title=dto.title,
            description=dto.description or "",
            file_path=s3_key,
            file_name=dto.file.name,
            file_size=dto.file.size,
            mime_type=dto.file.content_type or 'application/octet-stream',
            tags=dto.tags or [],
            metadata=dto.metadata or {}
        )
        
        return self._to_dto(document)
    
    def list_documents(self, include_archived: bool = False) -> List[DocumentDTO]:
        """
        List documents for the current tenant.
        """
        queryset = Document.objects.filter(tenant=self.tenant)
        if not include_archived:
            queryset = queryset.filter(is_archived=False)
        
        return [self._to_dto(doc) for doc in queryset]
    
    def get_document(self, document_id: int) -> Optional[DocumentDTO]:
        """
        Get a specific document.
        """
        try:
            document = Document.objects.get(
                id=document_id,
                tenant=self.tenant
            )
            return self._to_dto(document)
        except Document.DoesNotExist:
            return None
    
    def archive_document(self, document_id: int) -> bool:
        """
        Archive a document.
        """
        updated = Document.objects.filter(
            id=document_id,
            tenant=self.tenant
        ).update(is_archived=True)
        
        return updated > 0
    
    def _generate_s3_key(self, filename: str, extension: str) -> str:
        """
        Generate S3 key with tenant isolation.
        Format: tenants/{tenant_id}/documents/{yyyy}/{mm}/{uuid}-{filename}
        """
        now = datetime.now()
        unique_id = uuid.uuid4().hex[:8]
        
        return f"tenants/{self.tenant.id}/documents/{now.year}/{now.month:02d}/{unique_id}-{filename}"
    
    def _to_dto(self, document: Document) -> DocumentDTO:
        """
        Convert Document model to DTO.
        """
        return DocumentDTO(
            id=document.id,
            title=document.title,
            file_name=document.file_name,
            file_size=document.file_size,
            mime_type=document.mime_type,
            created_at=document.created_at,
            tags=document.tags
        )