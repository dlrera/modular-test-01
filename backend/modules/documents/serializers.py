"""
Document serializers for API.
"""
from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for Document model.
    """
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'description', 'file_path', 'file_name',
            'file_size', 'mime_type', 'tags', 'metadata',
            'is_archived', 'created_at', 'updated_at',
            'created_by_name'
        ]
        read_only_fields = ['tenant', 'created_by', 'created_at', 'updated_at']


class DocumentUploadSerializer(serializers.Serializer):
    """
    Serializer for document upload.
    """
    file = serializers.FileField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    tags = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list
    )