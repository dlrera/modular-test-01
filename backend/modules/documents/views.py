"""
Document Management API Views

This module provides RESTful API endpoints for document management operations,
including file upload/download, folder management, sharing, and notifications.
All views enforce tenant isolation and role-based permissions.

Author: Development Team  
Date: December 2024
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Count
from django.db import transaction
from django.utils import timezone
from core.tenancy.views import TenantAwareViewSet
from core.auth.permissions import RoleBasedPermission
from .models import (
    Document, Folder, DocumentShare, 
    ShareNotification, FolderUserState
)
from .serializers import (
    DocumentSerializer, DocumentUploadSerializer,
    FolderSerializer, DocumentShareSerializer,
    ShareNotificationSerializer, FolderStateSerializer,
    DocumentSearchSerializer
)
from .storage import document_storage
import os
import uuid


class FolderViewSet(TenantAwareViewSet):
    """API viewset for folder management"""
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [RoleBasedPermission]
    
    role_permissions = {
        'list': ['user', 'manager', 'admin'],
        'retrieve': ['user', 'manager', 'admin'],
        'create': ['user', 'manager', 'admin'],
        'update': ['manager', 'admin'],
        'partial_update': ['manager', 'admin'],
        'destroy': ['admin'],
        'toggle_expand': ['user', 'manager', 'admin'],
    }
    
    def get_queryset(self):
        """Filter folders by tenant"""
        queryset = super().get_queryset()
        
        # Filter root folders if no parent specified
        parent_id = self.request.query_params.get('parent')
        if parent_id == 'root':
            queryset = queryset.filter(parent__isnull=True)
        elif parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        
        return queryset.order_by('name')
    
    def perform_create(self, serializer):
        """Set created_by when creating folder"""
        serializer.save(
            created_by=self.request.user,
            tenant=self.request.tenant
        )
    
    @action(detail=True, methods=['post'])
    def toggle_expand(self, request, pk=None):
        """Toggle folder expand/collapse state for user"""
        folder = self.get_object()
        
        state, created = FolderUserState.objects.update_or_create(
            user=request.user,
            folder=folder,
            defaults={'is_expanded': not folder.user_states.filter(
                user=request.user
            ).first().is_expanded if folder.user_states.filter(
                user=request.user
            ).exists() else True}
        )
        
        return Response({'is_expanded': state.is_expanded})
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get entire folder tree structure"""
        root_folders = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(root_folders, many=True)
        return Response(serializer.data)


class DocumentViewSet(TenantAwareViewSet):
    """API viewset for document management"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [RoleBasedPermission]
    parser_classes = [MultiPartParser, FormParser]
    
    role_permissions = {
        'list': ['user', 'manager', 'admin'],
        'retrieve': ['user', 'manager', 'admin'],
        'create': ['user', 'manager', 'admin'],
        'update': ['manager', 'admin'],
        'partial_update': ['manager', 'admin'],
        'destroy': ['admin'],
        'upload': ['user', 'manager', 'admin'],
        'archive': ['manager', 'admin'],
        'restore': ['manager', 'admin'],
        'download_url': ['user', 'manager', 'admin'],
        'search': ['user', 'manager', 'admin'],
    }
    
    def get_queryset(self):
        """Filter documents by tenant and apply filters"""
        queryset = super().get_queryset()
        
        # Filter by folder if specified
        folder_id = self.request.query_params.get('folder')
        if folder_id:
            if folder_id == 'root':
                queryset = queryset.filter(folder__isnull=True)
            else:
                queryset = queryset.filter(folder_id=folder_id)
        
        # Filter by archived status
        show_archived = self.request.query_params.get('archived', 'false').lower() == 'true'
        queryset = queryset.filter(is_archived=show_archived)
        
        # Include shared documents
        include_shared = self.request.query_params.get('include_shared', 'true').lower() == 'true'
        if include_shared:
            # Get documents shared with current user
            shared_docs = DocumentShare.objects.filter(
                shared_with=self.request.user,
                status='accepted',
                tenant=self.request.tenant
            ).values_list('document_id', flat=True)
            
            queryset = queryset.filter(
                Q(created_by=self.request.user) | Q(id__in=shared_docs)
            )
        else:
            queryset = queryset.filter(created_by=self.request.user)
        
        # Sorting
        sort_by = self.request.query_params.get('sort', 'name')
        if sort_by == 'date':
            queryset = queryset.order_by('-created_at')
        elif sort_by == 'size':
            queryset = queryset.order_by('-file_size')
        else:
            queryset = queryset.order_by('nickname', 'original_name')
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload a new document"""
        serializer = DocumentUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        file = serializer.validated_data['file']
        folder = serializer.validated_data.get('folder')
        
        # Validate file
        file_extension = os.path.splitext(file.name)[1]
        is_valid, error_msg = document_storage.validate_file_upload(
            file.size,
            file_extension,
            file.content_type
        )
        
        if not is_valid:
            return Response(
                {'error': error_msg},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate document ID and S3 key
        document_id = str(uuid.uuid4())
        tenant_id = str(request.tenant.id)
        s3_key = document_storage.generate_s3_key(tenant_id, file.name, document_id)
        
        # Upload to S3
        file_content = file.read()
        upload_result = document_storage.upload_file(
            file_content,
            s3_key,
            content_type=file.content_type,
            metadata={
                'uploaded_by': str(request.user.id),
                'original_name': file.name,
                'tenant_id': tenant_id
            }
        )
        
        if not upload_result['success']:
            return Response(
                {'error': 'Failed to upload file'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create document record
        with transaction.atomic():
            document = Document.objects.create(
                id=document_id,
                tenant=request.tenant,
                folder=folder,
                original_name=file.name,
                nickname=serializer.validated_data.get('nickname', ''),
                description=serializer.validated_data.get('description', ''),
                file_size=file.size,
                file_extension=file_extension,
                mime_type=file.content_type,
                s3_key=s3_key,
                s3_bucket=document_storage.bucket_name,
                s3_version_id=upload_result.get('version_id', ''),
                created_by=request.user
            )
            
            # Create shares if specified
            share_with_users = serializer.validated_data.get('share_with', [])
            for user in share_with_users:
                share = DocumentShare.objects.create(
                    tenant=request.tenant,
                    document=document,
                    shared_by=request.user,
                    shared_with=user,
                    created_by=request.user
                )
                
                # Create notification
                ShareNotification.objects.create(
                    tenant=request.tenant,
                    recipient=user,
                    document_share=share,
                    notification_type='share_received',
                    created_by=request.user
                )
        
        response_serializer = DocumentSerializer(document, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a document"""
        document = self.get_object()
        
        # Move file to archive in S3
        archive_result = document_storage.move_to_archive(document.s3_key)
        
        if archive_result['success']:
            document.is_archived = True
            document.archived_at = timezone.now()
            document.s3_key = archive_result['archived_key']
            document.save()
            
            return Response({'status': 'archived'})
        else:
            return Response(
                {'error': 'Failed to archive document'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore an archived document"""
        document = self.get_object()
        
        if not document.is_archived:
            return Response(
                {'error': 'Document is not archived'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Move file back from archive
        original_key = document.s3_key.replace('/archive/', '/documents/', 1)
        restore_result = document_storage.copy_file(document.s3_key, original_key)
        
        if restore_result['success']:
            document_storage.delete_file(document.s3_key)
            document.is_archived = False
            document.archived_at = None
            document.s3_key = original_key
            document.save()
            
            return Response({'status': 'restored'})
        else:
            return Response(
                {'error': 'Failed to restore document'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def download_url(self, request, pk=None):
        """Get pre-signed download URL"""
        document = self.get_object()
        
        # Check if user has access
        can_access = (
            document.created_by == request.user or
            document.shares.filter(
                shared_with=request.user,
                status='accepted',
                can_download=True
            ).exists()
        )
        
        if not can_access:
            return Response(
                {'error': 'No permission to download this document'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        url = document_storage.generate_presigned_download_url(
            document.s3_key,
            expiration=3600,
            filename=document.display_name + document.file_extension
        )
        
        return Response({'download_url': url})
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search documents"""
        serializer = DocumentSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        query = serializer.validated_data['query'].lower()
        include_description = serializer.validated_data['include_description']
        
        # Build search query
        queryset = self.get_queryset()
        
        # Search in names
        search_q = Q(original_name__icontains=query) | Q(nickname__icontains=query)
        
        # Include description if requested
        if include_description:
            search_q |= Q(description__icontains=query)
        
        queryset = queryset.filter(search_q)
        
        # Filter by folder if specified
        folder_id = serializer.validated_data.get('folder')
        if folder_id:
            queryset = queryset.filter(folder_id=folder_id)
        
        # Filter by file types if specified
        file_types = serializer.validated_data.get('file_types')
        if file_types:
            queryset = queryset.filter(file_type__in=file_types)
        
        # Filter by archived status
        queryset = queryset.filter(
            is_archived=serializer.validated_data['archived']
        )
        
        # Serialize results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = DocumentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = DocumentSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class DocumentShareViewSet(TenantAwareViewSet):
    """API viewset for document sharing"""
    queryset = DocumentShare.objects.all()
    serializer_class = DocumentShareSerializer
    permission_classes = [RoleBasedPermission]
    
    role_permissions = {
        'list': ['user', 'manager', 'admin'],
        'retrieve': ['user', 'manager', 'admin'],
        'create': ['user', 'manager', 'admin'],
        'destroy': ['user', 'manager', 'admin'],
        'accept': ['user', 'manager', 'admin'],
        'reject': ['user', 'manager', 'admin'],
        'revoke': ['user', 'manager', 'admin'],
    }
    
    def get_queryset(self):
        """Filter shares by user"""
        queryset = super().get_queryset()
        
        # Get filter type
        filter_type = self.request.query_params.get('type', 'received')
        
        if filter_type == 'sent':
            queryset = queryset.filter(shared_by=self.request.user)
        else:  # received
            queryset = queryset.filter(shared_with=self.request.user)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-shared_at')
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a share invitation"""
        share = self.get_object()
        
        if share.shared_with != request.user:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if share.status != 'pending':
            return Response(
                {'error': 'Share is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        share.accept()
        
        # Create notification for sharer
        ShareNotification.objects.create(
            tenant=share.tenant,
            recipient=share.shared_by,
            document_share=share,
            notification_type='share_accepted',
            created_by=request.user
        )
        
        return Response({'status': 'accepted'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a share invitation"""
        share = self.get_object()
        
        if share.shared_with != request.user:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if share.status != 'pending':
            return Response(
                {'error': 'Share is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        share.reject()
        
        # Create notification for sharer
        ShareNotification.objects.create(
            tenant=share.tenant,
            recipient=share.shared_by,
            document_share=share,
            notification_type='share_rejected',
            created_by=request.user
        )
        
        return Response({'status': 'rejected'})
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a share"""
        share = self.get_object()
        
        if share.shared_by != request.user:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if share.status == 'revoked':
            return Response(
                {'error': 'Share already revoked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        share.revoke()
        
        # Create notification for recipient
        ShareNotification.objects.create(
            tenant=share.tenant,
            recipient=share.shared_with,
            document_share=share,
            notification_type='share_revoked',
            created_by=request.user
        )
        
        return Response({'status': 'revoked'})


class ShareNotificationViewSet(TenantAwareViewSet):
    """API viewset for share notifications"""
    queryset = ShareNotification.objects.all()
    serializer_class = ShareNotificationSerializer
    permission_classes = [RoleBasedPermission]
    
    role_permissions = {
        'list': ['user', 'manager', 'admin'],
        'retrieve': ['user', 'manager', 'admin'],
        'mark_read': ['user', 'manager', 'admin'],
        'mark_all_read': ['user', 'manager', 'admin'],
        'unread_count': ['user', 'manager', 'admin'],
    }
    
    def get_queryset(self):
        """Filter notifications by recipient"""
        queryset = super().get_queryset()
        queryset = queryset.filter(recipient=self.request.user)
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        
        if notification.recipient != request.user:
            return Response(
                {'error': 'Not authorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.mark_as_read()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        notifications = self.get_queryset().filter(is_read=False)
        count = notifications.update(is_read=True, read_at=timezone.now())
        
        return Response({'marked_read': count})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications"""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})