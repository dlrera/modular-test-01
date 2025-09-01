"""
Document Management Models

This module defines the core data models for the document management system,
including folders, documents, sharing, and notifications. All models inherit
from TenantBaseModel to ensure proper tenant isolation.

Author: Development Team
Date: December 2024
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from core.tenancy.models import TenantBaseModel
import uuid
from typing import Optional

User = get_user_model()


class Folder(TenantBaseModel):
    """Hierarchical folder structure for organizing documents"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True
    )
    # Temporary field for testing without user authentication
    # TODO: Remove when using FolderUserState with proper authentication
    is_expanded = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'documents_folders'
        ordering = ['name']
        unique_together = [['tenant', 'parent', 'name']]
        indexes = [
            models.Index(fields=['tenant', 'parent']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return self.name
    
    def get_full_path(self) -> str:
        """Get the full path from root to this folder"""
        if self.parent:
            return f"{self.parent.get_full_path()}/{self.name}"
        return self.name
    
    def get_ancestors(self) -> models.QuerySet:
        """Get all parent folders up to root"""
        ancestors = []
        parent = self.parent
        while parent:
            ancestors.append(parent)
            parent = parent.parent
        return ancestors
    
    def get_descendants(self) -> models.QuerySet:
        """Get all child folders recursively"""
        descendants = []
        children = self.children.all()
        for child in children:
            descendants.append(child)
            descendants.extend(child.get_descendants())
        return descendants


class Document(TenantBaseModel):
    """Document metadata with S3 storage references"""
    
    FILE_TYPE_CHOICES = [
        ('word', 'Microsoft Word'),
        ('excel', 'Microsoft Excel'),
        ('pdf', 'PDF'),
        ('image', 'Image'),
        ('csv', 'CSV'),
        ('text', 'Text'),
        ('generic', 'Generic'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    
    # File metadata
    original_name = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES, default='generic')
    mime_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField()  # Size in bytes
    file_extension = models.CharField(max_length=10)
    
    # S3 storage references
    s3_key = models.CharField(max_length=500, unique=True)
    s3_bucket = models.CharField(max_length=255)
    s3_version_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Additional metadata
    is_archived = models.BooleanField(default=False)
    archived_at = models.DateTimeField(null=True, blank=True)
    
    # Search optimization
    search_vector = models.TextField(blank=True)  # For full-text search
    
    # AI processing flags (future feature)
    ai_processed = models.BooleanField(default=False)
    ai_processed_at = models.DateTimeField(null=True, blank=True)
    ai_metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'documents_documents'
        ordering = ['nickname', 'original_name']
        indexes = [
            models.Index(fields=['tenant', 'folder']),
            models.Index(fields=['created_at']),
            models.Index(fields=['created_by']),
            models.Index(fields=['file_type']),
            models.Index(fields=['is_archived']),
        ]
    
    def __str__(self) -> str:
        return self.display_name
    
    @property
    def display_name(self) -> str:
        """Return nickname if available, otherwise original name without extension"""
        if self.nickname:
            return self.nickname
        # Remove file extension from display
        name_without_ext = self.original_name.rsplit('.', 1)[0] if '.' in self.original_name else self.original_name
        return name_without_ext
    
    def get_s3_url(self, expiration: int = 3600) -> str:
        """Generate pre-signed S3 URL for download"""
        # TODO: Implement proper S3 presigned URL generation
        # For now, return a mock URL for testing
        if self.s3_key:
            return f"http://localhost:9000/{self.s3_bucket}/{self.s3_key}"
        return ""
    
    def determine_file_type(self) -> str:
        """Determine file type based on extension and mime type"""
        ext = self.file_extension.lower()
        mime = self.mime_type.lower()
        
        if ext in ['doc', 'docx'] or 'word' in mime:
            return 'word'
        elif ext in ['xls', 'xlsx'] or 'excel' in mime or 'spreadsheet' in mime:
            return 'excel'
        elif ext == 'pdf' or 'pdf' in mime:
            return 'pdf'
        elif ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'] or 'image' in mime:
            return 'image'
        elif ext == 'csv' or 'csv' in mime:
            return 'csv'
        elif ext in ['txt', 'md'] or 'text' in mime:
            return 'text'
        else:
            return 'generic'
    
    def save(self, *args, **kwargs):
        """Auto-determine file type before saving"""
        if not self.file_type or self.file_type == 'generic':
            self.file_type = self.determine_file_type()
        
        # Update search vector for full-text search
        self.search_vector = f"{self.original_name} {self.nickname} {self.description}".lower()
        
        super().save(*args, **kwargs)


class DocumentShare(TenantBaseModel):
    """Sharing relationships between users for documents"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('revoked', 'Revoked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='shares'
    )
    shared_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents_shared_by_me'
    )
    shared_with = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents_shared_with_me'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Permissions
    can_download = models.BooleanField(default=True)
    can_share = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    
    # Tracking
    shared_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Optional message
    message = models.TextField(blank=True)
    
    class Meta:
        db_table = 'documents_shares'
        unique_together = [['document', 'shared_with']]
        indexes = [
            models.Index(fields=['tenant', 'shared_with', 'status']),
            models.Index(fields=['shared_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.document.display_name} shared with {self.shared_with}"
    
    def accept(self) -> None:
        """Accept the share invitation"""
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
    
    def reject(self) -> None:
        """Reject the share invitation"""
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.save()
    
    def revoke(self) -> None:
        """Revoke the share"""
        self.status = 'revoked'
        self.save()
    
    def is_expired(self) -> bool:
        """Check if the share has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class ShareNotification(TenantBaseModel):
    """Notifications for document sharing"""
    
    TYPE_CHOICES = [
        ('share_received', 'Document Shared With You'),
        ('share_accepted', 'Share Accepted'),
        ('share_rejected', 'Share Rejected'),
        ('share_revoked', 'Share Revoked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_notifications'
    )
    document_share = models.ForeignKey(
        DocumentShare,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    
    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'documents_notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.notification_type} for {self.recipient}"
    
    def mark_as_read(self) -> None:
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class FolderUserState(TenantBaseModel):
    """Track user-specific folder states (expanded/collapsed)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='folder_states'
    )
    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        related_name='user_states'
    )
    is_expanded = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'documents_folder_states'
        unique_together = [['user', 'folder']]
        indexes = [
            models.Index(fields=['user', 'folder']),
        ]
    
    def __str__(self) -> str:
        return f"{self.user} - {self.folder.name} ({'expanded' if self.is_expanded else 'collapsed'})"