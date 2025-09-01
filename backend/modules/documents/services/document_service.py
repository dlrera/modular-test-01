from dataclasses import dataclass
from typing import List, Optional, BinaryIO
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
import uuid
import os

from ..models import Document, Folder, DocumentShare, ShareNotification
from ..storage import document_storage


@dataclass
class DocumentDTO:
    """Data transfer object for document information"""
    id: str
    original_name: str
    nickname: str
    display_name: str
    description: str
    file_type: str
    file_size: int
    folder_id: Optional[str]
    folder_path: str
    download_url: str
    is_archived: bool
    created_at: str
    created_by_name: str


@dataclass
class FolderDTO:
    """Data transfer object for folder information"""
    id: str
    name: str
    parent_id: Optional[str]
    full_path: str
    document_count: int
    is_expanded: bool
    children: List['FolderDTO']


@dataclass
class UploadDocumentDTO:
    """Input DTO for document upload"""
    file: UploadedFile
    folder_id: Optional[str]
    nickname: Optional[str]
    description: Optional[str]
    share_with_user_ids: List[str]


@dataclass
class ShareDocumentDTO:
    """Input DTO for sharing a document"""
    document_id: str
    user_ids: List[str]
    can_download: bool = True
    can_share: bool = False
    can_edit: bool = False
    message: Optional[str] = None


@dataclass
class SearchDocumentDTO:
    """Input DTO for document search"""
    query: str
    include_description: bool = False
    folder_id: Optional[str] = None
    file_types: List[str] = None
    archived: bool = False


class DocumentService:
    """Service layer for document management operations"""
    
    def __init__(self, user, tenant):
        self.user = user
        self.tenant = tenant
    
    @transaction.atomic
    def upload_document(self, dto: UploadDocumentDTO) -> DocumentDTO:
        """Upload a new document with metadata and optional sharing"""
        
        # Validate file
        file_extension = os.path.splitext(dto.file.name)[1]
        is_valid, error_msg = document_storage.validate_file_upload(
            dto.file.size,
            file_extension,
            dto.file.content_type
        )
        
        if not is_valid:
            raise ValueError(error_msg)
        
        # Generate document ID and S3 key
        document_id = str(uuid.uuid4())
        s3_key = document_storage.generate_s3_key(
            str(self.tenant.id),
            dto.file.name,
            document_id
        )
        
        # Upload to S3
        file_content = dto.file.read()
        upload_result = document_storage.upload_file(
            file_content,
            s3_key,
            content_type=dto.file.content_type,
            metadata={
                'uploaded_by': str(self.user.id),
                'original_name': dto.file.name,
                'tenant_id': str(self.tenant.id)
            }
        )
        
        if not upload_result['success']:
            raise Exception("Failed to upload file to storage")
        
        # Get folder if specified
        folder = None
        if dto.folder_id:
            folder = Folder.objects.filter(
                id=dto.folder_id,
                tenant=self.tenant
            ).first()
        
        # Create document record
        document = Document.objects.create(
            id=document_id,
            tenant=self.tenant,
            folder=folder,
            original_name=dto.file.name,
            nickname=dto.nickname or '',
            description=dto.description or '',
            file_size=dto.file.size,
            file_extension=file_extension,
            mime_type=dto.file.content_type,
            s3_key=s3_key,
            s3_bucket=document_storage.bucket_name,
            s3_version_id=upload_result.get('version_id', ''),
            created_by=self.user
        )
        
        # Create shares if specified
        for user_id in dto.share_with_user_ids:
            self._create_share(document, user_id)
        
        return self._document_to_dto(document)
    
    def archive_document(self, document_id: str) -> bool:
        """Archive a document"""
        document = Document.objects.filter(
            id=document_id,
            tenant=self.tenant
        ).first()
        
        if not document:
            return False
        
        # Move to archive in S3
        archive_result = document_storage.move_to_archive(document.s3_key)
        
        if archive_result['success']:
            document.is_archived = True
            document.archived_at = timezone.now()
            document.s3_key = archive_result['archived_key']
            document.save()
            return True
        
        return False
    
    @transaction.atomic
    def share_document(self, dto: ShareDocumentDTO) -> bool:
        """Share a document with specified users"""
        document = Document.objects.filter(
            id=dto.document_id,
            tenant=self.tenant
        ).first()
        
        if not document:
            return False
        
        # Check if user can share
        can_share = (
            document.created_by == self.user or
            document.shares.filter(
                shared_with=self.user,
                status='accepted',
                can_share=True
            ).exists()
        )
        
        if not can_share:
            raise PermissionError("You don't have permission to share this document")
        
        # Create shares
        for user_id in dto.user_ids:
            share = DocumentShare.objects.create(
                tenant=self.tenant,
                document=document,
                shared_by=self.user,
                shared_with_id=user_id,
                can_download=dto.can_download,
                can_share=dto.can_share,
                can_edit=dto.can_edit,
                message=dto.message,
                created_by=self.user
            )
            
            # Create notification
            ShareNotification.objects.create(
                tenant=self.tenant,
                recipient_id=user_id,
                document_share=share,
                notification_type='share_received',
                created_by=self.user
            )
        
        return True
    
    def search_documents(self, dto: SearchDocumentDTO) -> List[DocumentDTO]:
        """Search documents based on criteria"""
        queryset = Document.objects.filter(tenant=self.tenant)
        
        # Apply search query
        if dto.include_description:
            queryset = queryset.filter(
                Q(original_name__icontains=dto.query) |
                Q(nickname__icontains=dto.query) |
                Q(description__icontains=dto.query)
            )
        else:
            queryset = queryset.filter(
                Q(original_name__icontains=dto.query) |
                Q(nickname__icontains=dto.query)
            )
        
        # Apply filters
        if dto.folder_id:
            queryset = queryset.filter(folder_id=dto.folder_id)
        
        if dto.file_types:
            queryset = queryset.filter(file_type__in=dto.file_types)
        
        queryset = queryset.filter(is_archived=dto.archived)
        
        # Include shared documents
        shared_docs = DocumentShare.objects.filter(
            shared_with=self.user,
            status='accepted',
            tenant=self.tenant
        ).values_list('document_id', flat=True)
        
        queryset = queryset.filter(
            Q(created_by=self.user) | Q(id__in=shared_docs)
        )
        
        return [self._document_to_dto(doc) for doc in queryset]
    
    def _document_to_dto(self, document: Document) -> DocumentDTO:
        """Convert document model to DTO"""
        return DocumentDTO(
            id=str(document.id),
            original_name=document.original_name,
            nickname=document.nickname,
            display_name=document.display_name,
            description=document.description,
            file_type=document.file_type,
            file_size=document.file_size,
            folder_id=str(document.folder.id) if document.folder else None,
            folder_path=document.folder.get_full_path() if document.folder else '/',
            download_url=document.get_s3_url(),
            is_archived=document.is_archived,
            created_at=document.created_at.isoformat(),
            created_by_name=document.created_by.get_full_name() if document.created_by else ''
        )
    
    def _create_share(self, document: Document, user_id: str) -> DocumentShare:
        """Create a document share with notification"""
        share = DocumentShare.objects.create(
            tenant=self.tenant,
            document=document,
            shared_by=self.user,
            shared_with_id=user_id,
            created_by=self.user
        )
        
        ShareNotification.objects.create(
            tenant=self.tenant,
            recipient_id=user_id,
            document_share=share,
            notification_type='share_received',
            created_by=self.user
        )
        
        return share