from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import (
    Document, Folder, DocumentShare, 
    ShareNotification, FolderUserState
)
from typing import List, Dict, Any

User = get_user_model()


class FolderSerializer(serializers.ModelSerializer):
    """Serializer for Folder model"""
    children = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()
    full_path = serializers.SerializerMethodField()
    is_expanded = serializers.SerializerMethodField()
    
    class Meta:
        model = Folder
        fields = [
            'id', 'name', 'parent', 'children', 'document_count',
            'full_path', 'is_expanded', 'created_at', 'updated_at'
        ]
        read_only_fields = ['tenant', 'created_by', 'created_at', 'updated_at']
    
    def get_children(self, obj) -> List[Dict]:
        """Get child folders"""
        children = obj.children.filter(tenant=obj.tenant)
        return FolderSerializer(children, many=True, context=self.context).data
    
    def get_document_count(self, obj) -> int:
        """Get count of documents in this folder"""
        return obj.documents.filter(tenant=obj.tenant, is_archived=False).count()
    
    def get_full_path(self, obj) -> str:
        """Get full path from root"""
        return obj.get_full_path()
    
    def get_is_expanded(self, obj) -> bool:
        """Get user's expand/collapse state for this folder"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            state = FolderUserState.objects.filter(
                user=request.user,
                folder=obj
            ).first()
            return state.is_expanded if state else False
        return False


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for Document model"""
    display_name = serializers.ReadOnlyField()
    uploaded_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    download_url = serializers.SerializerMethodField()
    folder_path = serializers.SerializerMethodField()
    shares = serializers.SerializerMethodField()
    can_share = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'folder', 'original_name', 'nickname', 'display_name',
            'description', 'file_type', 'mime_type', 'file_size',
            'file_extension', 'download_url', 'folder_path',
            'uploaded_by_name', 'shares', 'can_share',
            'is_archived', 'archived_at', 'ai_processed',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'tenant', 'created_by', 's3_key', 's3_bucket', 
            's3_version_id', 'created_at', 'updated_at',
            'file_type', 'search_vector'
        ]
    
    def get_download_url(self, obj) -> str:
        """Generate pre-signed download URL"""
        return obj.get_s3_url()
    
    def get_folder_path(self, obj) -> str:
        """Get folder path"""
        return obj.folder.get_full_path() if obj.folder else '/'
    
    def get_shares(self, obj) -> List[Dict]:
        """Get active shares for this document"""
        request = self.context.get('request')
        if request and request.user == obj.created_by:
            shares = obj.shares.filter(status__in=['pending', 'accepted'])
            return DocumentShareSerializer(shares, many=True).data
        return []
    
    def get_can_share(self, obj) -> bool:
        """Check if current user can share this document"""
        request = self.context.get('request')
        if not request:
            return False
        
        # For testing without authentication, allow sharing
        # TODO: Re-enable user permission checks when authentication is configured
        from django.contrib.auth.models import AnonymousUser
        if isinstance(request.user, AnonymousUser):
            return True
        
        # Owner can always share
        if request.user == obj.created_by:
            return True
        
        # Check if user has share permission
        share = obj.shares.filter(
            shared_with=request.user,
            status='accepted',
            can_share=True
        ).first()
        
        return bool(share)


class DocumentUploadSerializer(serializers.Serializer):
    """Serializer for document upload"""
    file = serializers.FileField()
    folder = serializers.UUIDField(required=False, allow_null=True)
    nickname = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    share_with = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list
    )
    
    def validate_folder(self, value):
        """Validate folder belongs to tenant"""
        if value:
            request = self.context.get('request')
            if request:
                try:
                    folder = Folder.objects.get(
                        id=value,
                        tenant=request.tenant
                    )
                    return folder
                except Folder.DoesNotExist:
                    raise serializers.ValidationError("Folder not found")
        return None
    
    def validate_share_with(self, value):
        """Validate users to share with"""
        if value:
            request = self.context.get('request')
            if request:
                # Get users in same tenant
                users = User.objects.filter(
                    id__in=value,
                    account__tenant=request.tenant
                ).exclude(id=request.user.id)
                
                if len(users) != len(value):
                    raise serializers.ValidationError("Some users not found")
                
                return users
        return []


class DocumentShareSerializer(serializers.ModelSerializer):
    """Serializer for DocumentShare model"""
    document_name = serializers.CharField(
        source='document.display_name',
        read_only=True
    )
    shared_by_name = serializers.CharField(
        source='shared_by.get_full_name',
        read_only=True
    )
    shared_with_name = serializers.CharField(
        source='shared_with.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = DocumentShare
        fields = [
            'id', 'document', 'document_name', 'shared_by', 'shared_by_name',
            'shared_with', 'shared_with_name', 'status',
            'can_download', 'can_share', 'can_edit',
            'message', 'shared_at', 'responded_at', 'expires_at'
        ]
        read_only_fields = [
            'tenant', 'shared_by', 'shared_at', 'responded_at'
        ]
    
    def validate(self, attrs):
        """Validate share creation"""
        request = self.context.get('request')
        if request:
            document = attrs.get('document')
            
            # Check if user can share this document
            if document.created_by != request.user:
                # Check if user has share permission
                share = document.shares.filter(
                    shared_with=request.user,
                    status='accepted',
                    can_share=True
                ).first()
                
                if not share:
                    raise serializers.ValidationError(
                        "You don't have permission to share this document"
                    )
            
            # Check if share already exists
            existing = DocumentShare.objects.filter(
                document=document,
                shared_with=attrs.get('shared_with')
            ).first()
            
            if existing:
                raise serializers.ValidationError(
                    "Document already shared with this user"
                )
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create share and notification"""
        request = self.context.get('request')
        validated_data['shared_by'] = request.user
        validated_data['tenant'] = request.tenant
        
        share = super().create(validated_data)
        
        # Create notification
        ShareNotification.objects.create(
            tenant=share.tenant,
            recipient=share.shared_with,
            document_share=share,
            notification_type='share_received',
            created_by=request.user
        )
        
        return share


class ShareNotificationSerializer(serializers.ModelSerializer):
    """Serializer for ShareNotification model"""
    document_name = serializers.CharField(
        source='document_share.document.display_name',
        read_only=True
    )
    shared_by_name = serializers.CharField(
        source='document_share.shared_by.get_full_name',
        read_only=True
    )
    share_status = serializers.CharField(
        source='document_share.status',
        read_only=True
    )
    
    class Meta:
        model = ShareNotification
        fields = [
            'id', 'document_share', 'document_name', 'shared_by_name',
            'notification_type', 'share_status', 'is_read', 'read_at',
            'created_at'
        ]
        read_only_fields = ['tenant', 'recipient', 'created_at']


class FolderStateSerializer(serializers.ModelSerializer):
    """Serializer for FolderUserState model"""
    
    class Meta:
        model = FolderUserState
        fields = ['folder', 'is_expanded']
        
    def create(self, validated_data):
        """Create or update folder state"""
        request = self.context.get('request')
        validated_data['user'] = request.user
        validated_data['tenant'] = request.tenant
        
        state, created = FolderUserState.objects.update_or_create(
            user=request.user,
            folder=validated_data['folder'],
            defaults={'is_expanded': validated_data['is_expanded']}
        )
        
        return state


class DocumentSearchSerializer(serializers.Serializer):
    """Serializer for document search"""
    query = serializers.CharField(required=True, min_length=2)
    include_description = serializers.BooleanField(default=False)
    folder = serializers.UUIDField(required=False, allow_null=True)
    file_types = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'word', 'excel', 'pdf', 'image', 'csv', 'text', 'generic'
        ]),
        required=False,
        default=list
    )
    archived = serializers.BooleanField(default=False)