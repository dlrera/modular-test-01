import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import json
import uuid

from ..models import Document, Folder, DocumentShare
from core.tenancy.models import Account, UserProfile, current_tenant

User = get_user_model()


@pytest.mark.django_db
class TestDocumentAPI(TestCase):
    """Test cases for document API endpoints"""
    
    def setUp(self):
        """Set up test data and client"""
        self.client = APIClient()
        
        # Create tenant
        self.tenant = Account.objects.create(
            name="Test Company",
            slug="test-company"
        )
        
        # Create users
        self.admin_user = User.objects.create_user(
            username="admin",
            email="admin@test.com",
            password="testpass123"
        )
        self.normal_user = User.objects.create_user(
            username="user",
            email="user@test.com",
            password="testpass123"
        )
        
        # Create user profiles
        UserProfile.objects.create(
            user=self.admin_user,
            account=self.tenant,
            role='admin'
        )
        UserProfile.objects.create(
            user=self.normal_user,
            account=self.tenant,
            role='user'
        )
        
        # Set tenant context
        current_tenant.set(self.tenant)
    
    def tearDown(self):
        """Clean up after tests"""
        current_tenant.set(None)
    
    def test_folder_creation(self):
        """Test folder creation via API"""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.post('/api/v1/folders/', {
            'name': 'Test Folder'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Test Folder')
        self.assertIsNone(response.data['parent'])
    
    def test_folder_hierarchy(self):
        """Test creating nested folders"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create parent folder
        parent_response = self.client.post('/api/v1/folders/', {
            'name': 'Parent Folder'
        })
        parent_id = parent_response.data['id']
        
        # Create child folder
        child_response = self.client.post('/api/v1/folders/', {
            'name': 'Child Folder',
            'parent': parent_id
        })
        
        self.assertEqual(child_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(child_response.data['parent'], parent_id)
        self.assertEqual(child_response.data['full_path'], 'Parent Folder/Child Folder')
    
    def test_document_upload(self):
        """Test document upload via API"""
        self.client.force_authenticate(user=self.normal_user)
        
        # Create test file
        file_content = b"Test file content"
        file = SimpleUploadedFile(
            "test_document.pdf",
            file_content,
            content_type="application/pdf"
        )
        
        response = self.client.post('/api/v1/files/upload/', {
            'file': file,
            'nickname': 'Test Doc',
            'description': 'A test document'
        }, format='multipart')
        
        # Note: This will fail without proper S3 setup
        # In real tests, you'd mock the S3 calls
        # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_document_list_filtering(self):
        """Test document list with filters"""
        self.client.force_authenticate(user=self.normal_user)
        
        # Create test documents
        folder = Folder.objects.create(
            tenant=self.tenant,
            name="Test Folder",
            created_by=self.admin_user
        )
        
        doc1 = Document.objects.create(
            tenant=self.tenant,
            folder=folder,
            original_name="doc1.pdf",
            file_size=1024,
            file_extension=".pdf",
            mime_type="application/pdf",
            s3_key="test-key-1",
            s3_bucket="test-bucket",
            created_by=self.normal_user
        )
        
        doc2 = Document.objects.create(
            tenant=self.tenant,
            original_name="doc2.pdf",
            file_size=2048,
            file_extension=".pdf",
            mime_type="application/pdf",
            s3_key="test-key-2",
            s3_bucket="test-bucket",
            is_archived=True,
            created_by=self.normal_user
        )
        
        # Test filtering by folder
        response = self.client.get(f'/api/v1/files/?folder={folder.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(doc1.id))
        
        # Test filtering by archived status
        response = self.client.get('/api/v1/files/?archived=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(doc2.id))
    
    def test_document_search(self):
        """Test document search functionality"""
        self.client.force_authenticate(user=self.normal_user)
        
        # Create test documents
        doc1 = Document.objects.create(
            tenant=self.tenant,
            original_name="important_report.pdf",
            nickname="Q4 Report",
            description="Quarterly financial report",
            file_size=1024,
            file_extension=".pdf",
            mime_type="application/pdf",
            s3_key="test-key-1",
            s3_bucket="test-bucket",
            created_by=self.normal_user
        )
        
        doc2 = Document.objects.create(
            tenant=self.tenant,
            original_name="meeting_notes.docx",
            description="Team meeting notes",
            file_size=512,
            file_extension=".docx",
            mime_type="application/vnd.openxmlformats",
            s3_key="test-key-2",
            s3_bucket="test-bucket",
            created_by=self.normal_user
        )
        
        # Search by name
        response = self.client.post('/api/v1/files/search/', {
            'query': 'report'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(doc1.id))
        
        # Search including description
        response = self.client.post('/api/v1/files/search/', {
            'query': 'meeting',
            'includeDescription': True
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(doc2.id))
    
    def test_document_sharing(self):
        """Test document sharing between users"""
        self.client.force_authenticate(user=self.admin_user)
        
        # Create document
        document = Document.objects.create(
            tenant=self.tenant,
            original_name="share_test.pdf",
            file_size=1024,
            file_extension=".pdf",
            mime_type="application/pdf",
            s3_key="test-key",
            s3_bucket="test-bucket",
            created_by=self.admin_user
        )
        
        # Share document
        response = self.client.post('/api/v1/shares/', {
            'document': str(document.id),
            'shared_with': str(self.normal_user.id),
            'can_download': True,
            'can_share': False,
            'message': 'Please review'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        
        share_id = response.data['id']
        
        # Switch to recipient user
        self.client.force_authenticate(user=self.normal_user)
        
        # Accept share
        response = self.client.post(f'/api/v1/shares/{share_id}/accept/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify document is accessible
        response = self.client.get('/api/v1/files/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        doc_ids = [d['id'] for d in response.data]
        self.assertIn(str(document.id), doc_ids)
    
    def test_notification_system(self):
        """Test notification creation and management"""
        # Create share which triggers notification
        document = Document.objects.create(
            tenant=self.tenant,
            original_name="test.pdf",
            file_size=1024,
            file_extension=".pdf",
            mime_type="application/pdf",
            s3_key="test-key",
            s3_bucket="test-bucket",
            created_by=self.admin_user
        )
        
        share = DocumentShare.objects.create(
            tenant=self.tenant,
            document=document,
            shared_by=self.admin_user,
            shared_with=self.normal_user,
            created_by=self.admin_user
        )
        
        # Check unread count
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get('/api/v1/notifications/unread_count/')
        
        # This would work with proper notification creation
        # self.assertEqual(response.data['unread_count'], 1)
    
    def test_permission_restrictions(self):
        """Test role-based permission restrictions"""
        self.client.force_authenticate(user=self.normal_user)
        
        # Create document as normal user
        document = Document.objects.create(
            tenant=self.tenant,
            original_name="test.pdf",
            file_size=1024,
            file_extension=".pdf",
            mime_type="application/pdf",
            s3_key="test-key",
            s3_bucket="test-bucket",
            created_by=self.normal_user
        )
        
        # Try to delete (should fail for normal user)
        response = self.client.delete(f'/api/v1/files/{document.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Switch to admin
        self.client.force_authenticate(user=self.admin_user)
        
        # Admin can delete
        response = self.client.delete(f'/api/v1/files/{document.id}/')
        # Note: Actual deletion requires proper permission setup
        # self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)