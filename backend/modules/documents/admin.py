from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Folder, Document, DocumentShare, 
    ShareNotification, FolderUserState
)


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'tenant', 'document_count', 'created_at']
    list_filter = ['tenant', 'created_at']
    search_fields = ['name']
    ordering = ['tenant', 'name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def document_count(self, obj):
        return obj.documents.count()
    document_count.short_description = 'Documents'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(tenant=request.user.account.tenant)
        return qs


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 'folder', 'file_type', 'file_size_formatted',
        'created_by', 'is_archived', 'created_at'
    ]
    list_filter = ['tenant', 'file_type', 'is_archived', 'ai_processed', 'created_at']
    search_fields = ['original_name', 'nickname', 'description']
    ordering = ['-created_at']
    readonly_fields = [
        'id', 's3_key', 's3_bucket', 's3_version_id',
        'file_type', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('original_name', 'nickname', 'description', 'folder')
        }),
        ('File Details', {
            'fields': (
                'file_type', 'mime_type', 'file_extension',
                'file_size', 's3_key', 's3_bucket', 's3_version_id'
            )
        }),
        ('Status', {
            'fields': ('is_archived', 'archived_at', 'ai_processed', 'ai_processed_at')
        }),
        ('Metadata', {
            'fields': ('tenant', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def file_size_formatted(self, obj):
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    file_size_formatted.short_description = 'Size'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(tenant=request.user.account.tenant)
        return qs


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = [
        'document', 'shared_by', 'shared_with', 'status',
        'can_download', 'can_share', 'can_edit', 'shared_at'
    ]
    list_filter = ['tenant', 'status', 'can_download', 'can_share', 'can_edit', 'shared_at']
    search_fields = ['document__original_name', 'document__nickname']
    ordering = ['-shared_at']
    readonly_fields = ['id', 'shared_at', 'responded_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(tenant=request.user.account.tenant)
        return qs


@admin.register(ShareNotification)
class ShareNotificationAdmin(admin.ModelAdmin):
    list_display = [
        'recipient', 'notification_type', 'document_name',
        'is_read', 'created_at'
    ]
    list_filter = ['tenant', 'notification_type', 'is_read', 'created_at']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'read_at']
    
    def document_name(self, obj):
        return obj.document_share.document.display_name
    document_name.short_description = 'Document'
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(tenant=request.user.account.tenant)
        return qs


@admin.register(FolderUserState)
class FolderUserStateAdmin(admin.ModelAdmin):
    list_display = ['user', 'folder', 'is_expanded', 'updated_at']
    list_filter = ['tenant', 'is_expanded', 'updated_at']
    ordering = ['user', 'folder']
    readonly_fields = ['id', 'updated_at']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(tenant=request.user.account.tenant)
        return qs