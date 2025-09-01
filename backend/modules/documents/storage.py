import boto3
import hashlib
import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from typing import Optional, Dict, Any, Tuple
from botocore.exceptions import ClientError
import mimetypes
from datetime import datetime, timedelta


class DocumentS3Storage:
    """Handle S3 operations for document storage"""
    
    def __init__(self):
        # For testing without S3
        self.s3_client = None
        self.bucket_name = 'test-bucket'
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None),  # For MinIO
                region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
            )
            self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        except Exception:
            pass  # S3 not configured, use mock mode
    
    def generate_s3_key(self, tenant_id: str, file_name: str, document_id: str) -> str:
        """Generate S3 key with tenant isolation and date organization"""
        now = timezone.now()
        # Remove file extension for cleaner paths
        base_name = os.path.splitext(file_name)[0]
        extension = os.path.splitext(file_name)[1]
        
        # Structure: tenants/{tenant_id}/documents/{year}/{month}/{document_id}/{filename}
        s3_key = f"tenants/{tenant_id}/documents/{now.year}/{now.month:02d}/{document_id}/{base_name}{extension}"
        return s3_key
    
    def upload_file(
        self,
        file_content: bytes,
        s3_key: str,
        content_type: str = None,
        metadata: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Upload file to S3 with metadata"""
        # Mock mode for testing without S3
        if not self.s3_client:
            return {
                'success': True,
                's3_key': s3_key,
                'version_id': 'mock-version',
                'etag': 'mock-etag',
                'file_hash': 'mock-hash'
            }
        
        try:
            extra_args = {}
            
            if content_type:
                extra_args['ContentType'] = content_type
            
            if metadata:
                extra_args['Metadata'] = metadata
            
            # Calculate file hash for integrity
            file_hash = hashlib.sha256(file_content).hexdigest()
            if not metadata:
                extra_args['Metadata'] = {}
            extra_args['Metadata']['sha256'] = file_hash
            
            # Upload to S3
            response = self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                **extra_args
            )
            
            return {
                'success': True,
                's3_key': s3_key,
                'version_id': response.get('VersionId'),
                'etag': response.get('ETag', '').strip('"'),
                'file_hash': file_hash
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_presigned_upload_url(
        self,
        s3_key: str,
        content_type: str = None,
        expiration: int = 3600
    ) -> Dict[str, Any]:
        """Generate pre-signed URL for direct browser upload"""
        try:
            # Generate the presigned POST URL
            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=s3_key,
                Fields={'Content-Type': content_type} if content_type else None,
                Conditions=[
                    ['content-length-range', 0, 104857600],  # Max 100MB
                ],
                ExpiresIn=expiration
            )
            
            return {
                'success': True,
                'url': response['url'],
                'fields': response['fields']
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_presigned_download_url(
        self,
        s3_key: str,
        expiration: int = 3600,
        filename: str = None
    ) -> str:
        """Generate pre-signed URL for file download"""
        try:
            params = {
                'Bucket': self.bucket_name,
                'Key': s3_key
            }
            
            if filename:
                params['ResponseContentDisposition'] = f'attachment; filename="{filename}"'
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params=params,
                ExpiresIn=expiration
            )
            
            return url
            
        except ClientError as e:
            return None
    
    def delete_file(self, s3_key: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
            
        except ClientError:
            return False
    
    def copy_file(self, source_key: str, destination_key: str) -> Dict[str, Any]:
        """Copy file within S3"""
        try:
            copy_source = {
                'Bucket': self.bucket_name,
                'Key': source_key
            }
            
            response = self.s3_client.copy_object(
                CopySource=copy_source,
                Bucket=self.bucket_name,
                Key=destination_key
            )
            
            return {
                'success': True,
                'new_key': destination_key,
                'version_id': response.get('VersionId')
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_metadata(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from S3"""
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return {
                'size': response['ContentLength'],
                'content_type': response.get('ContentType'),
                'last_modified': response['LastModified'],
                'etag': response.get('ETag', '').strip('"'),
                'metadata': response.get('Metadata', {}),
                'version_id': response.get('VersionId')
            }
            
        except ClientError:
            return None
    
    def list_folder_contents(self, tenant_id: str, folder_path: str = '') -> Dict[str, Any]:
        """List all files in a folder for a tenant"""
        prefix = f"tenants/{tenant_id}/documents/"
        if folder_path:
            prefix += folder_path.strip('/') + '/'
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                Delimiter='/'
            )
            
            files = []
            folders = []
            
            # Process files
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified']
                })
            
            # Process folders (common prefixes)
            for prefix_info in response.get('CommonPrefixes', []):
                folder_name = prefix_info['Prefix'].rstrip('/').split('/')[-1]
                folders.append(folder_name)
            
            return {
                'success': True,
                'files': files,
                'folders': folders
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_file_upload(
        self,
        file_size: int,
        file_extension: str,
        mime_type: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate file before upload"""
        
        # Check file size (max 100MB)
        max_size = 104857600  # 100MB in bytes
        if file_size > max_size:
            return False, f"File size exceeds maximum allowed size of {max_size / 1048576}MB"
        
        # Check file extension against blocked list
        blocked_extensions = [
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
            '.vbs', '.js', '.jar', '.msi', '.app', '.deb', '.rpm'
        ]
        if file_extension.lower() in blocked_extensions:
            return False, f"File type {file_extension} is not allowed"
        
        # Validate mime type
        if not mime_type:
            mime_type, _ = mimetypes.guess_type(f"file{file_extension}")
            if not mime_type:
                return False, "Could not determine file type"
        
        return True, None
    
    def generate_thumbnail_key(self, original_key: str) -> str:
        """Generate S3 key for thumbnail"""
        parts = original_key.rsplit('.', 1)
        if len(parts) == 2:
            return f"{parts[0]}_thumb.jpg"
        return f"{original_key}_thumb.jpg"
    
    def move_to_archive(self, s3_key: str) -> Dict[str, Any]:
        """Move file to archive folder"""
        # Replace 'documents' with 'archive' in the path
        archive_key = s3_key.replace('/documents/', '/archive/', 1)
        
        result = self.copy_file(s3_key, archive_key)
        if result['success']:
            self.delete_file(s3_key)
            result['archived_key'] = archive_key
        
        return result


# Initialize storage instance
document_storage = DocumentS3Storage()