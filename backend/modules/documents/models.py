"""
Document management models.
"""
from django.db import models
from core.tenancy.models import TenantBaseModel


class Document(TenantBaseModel):
    """
    Represents a document uploaded by a tenant.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file_path = models.CharField(max_length=500)  # S3 key
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # Size in bytes
    mime_type = models.CharField(max_length=100)
    
    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Status
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tenant', 'is_archived']),
            models.Index(fields=['tenant', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.file_name})"