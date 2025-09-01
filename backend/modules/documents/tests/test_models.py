import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

from ..models import Document, Folder, DocumentShare, ShareNotification, FolderUserState
from core.tenancy.models import Account, UserProfile

User = get_user_model()


@pytest.mark.django_db
class TestDocumentModels(TestCase):
    """Test cases for document models"""
    
    def setUp(self):
        """Set up test data"""
        # Create tenant
        self.tenant = Account.objects.create(
            name="Test Company",
            slug="test-company"
        )
        
        # Create users
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@test.com",
            password="testpass123"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@test.com",
            password="testpass123"
        )
        
        # Create user profiles
        UserProfile.objects.create(
            user=self.user1,
            account=self.tenant,
            role='admin'
        )
        UserProfile.objects.create(
            user=self.user2,
            account=self.tenant,
            role='user'
        )
    
    def test_folder_creation(self):
        """Test folder creation and hierarchy"""
        # Create root folder
        root_folder = Folder.objects.create(
            tenant=self.tenant,
            name="Root Folder",
            created_by=self.user1
        )
        
        # Create subfolder
        subfolder = Folder.objects.create(
            tenant=self.tenant,
            name="Subfolder",
            parent=root_folder,
            created_by=self.user1
        )
        
        # Test relationships
        self.assertEqual(subfolder.parent, root_folder)
        self.assertIn(subfolder, root_folder.children.all())
        
        # Test full path
        self.assertEqual(root_folder.get_full_path(), "Root Folder")
        self.assertEqual(subfolder.get_full_path(), "Root Folder/Subfolder")
        
        # Test ancestors
        ancestors = subfolder.get_ancestors()
        self.assertEqual(len(ancestors), 1)
        self.assertEqual(ancestors[0], root_folder)
    
    def test_document_creation(self):
        """Test document creation and properties"""
        document = Document.objects.create(
            tenant=self.tenant,
            original_name="test_document.pdf",
            nickname="Test Doc",
            description="A test document",
            file_size=1024000,
            file_extension=".pdf",
            mime_type="application/pdf",
            s3_key=f"tenants/{self.tenant.id}/documents/2024/01/{uuid.uuid4()}/test.pdf",
            s3_bucket="test-bucket",
            created_by=self.user1
        )
        
        # Test display name
        self.assertEqual(document.display_name, "Test Doc")
        
        # Test file type detection
        self.assertEqual(document.file_type, "pdf")
        
        # Test without nickname
        document.nickname = ""
        document.save()
        self.assertEqual(document.display_name, "test_document")
    
    def test_document_share(self):
        """Test document sharing functionality"""
        document = Document.objects.create(
            tenant=self.tenant,
            original_name="shared_doc.pdf",
            file_size=1024,
            file_extension=".pdf",
            mime_type="application/pdf",
            s3_key=f"tenants/{self.tenant.id}/documents/test.pdf",
            s3_bucket="test-bucket",
            created_by=self.user1
        )
        
        # Create share
        share = DocumentShare.objects.create(
            tenant=self.tenant,
            document=document,
            shared_by=self.user1,
            shared_with=self.user2,
            can_download=True,
            can_share=False,
            can_edit=False,
            message="Please review this document",
            created_by=self.user1
        )
        
        # Test initial status
        self.assertEqual(share.status, 'pending')
        
        # Test accept
        share.accept()
        self.assertEqual(share.status, 'accepted')
        self.assertIsNotNone(share.responded_at)
        
        # Test unique constraint
        with self.assertRaises(Exception):
            DocumentShare.objects.create(
                tenant=self.tenant,
                document=document,
                shared_by=self.user1,
                shared_with=self.user2,
                created_by=self.user1
            )
    
    def test_share_expiration(self):
        """Test share expiration functionality"""
        document = Document.objects.create(
            tenant=self.tenant,
            original_name="test.pdf",
            file_size=1024,
            file_extension=".pdf",
            mime_type="application/pdf",
            s3_key="test-key",
            s3_bucket="test-bucket",
            created_by=self.user1
        )
        
        # Create expired share
        expired_share = DocumentShare.objects.create(
            tenant=self.tenant,
            document=document,
            shared_by=self.user1,
            shared_with=self.user2,
            expires_at=timezone.now() - timedelta(days=1),
            created_by=self.user1
        )
        
        self.assertTrue(expired_share.is_expired())
        
        # Create valid share
        valid_share = DocumentShare.objects.create(
            tenant=self.tenant,
            document=document,
            shared_by=self.user1,
            shared_with=User.objects.create_user("user3", "user3@test.com"),
            expires_at=timezone.now() + timedelta(days=1),
            created_by=self.user1
        )
        
        self.assertFalse(valid_share.is_expired())
    
    def test_share_notification(self):
        """Test share notification creation"""
        document = Document.objects.create(
            tenant=self.tenant,
            original_name="test.pdf",
            file_size=1024,
            file_extension=".pdf",
            mime_type="application/pdf",
            s3_key="test-key",
            s3_bucket="test-bucket",
            created_by=self.user1
        )
        
        share = DocumentShare.objects.create(
            tenant=self.tenant,
            document=document,
            shared_by=self.user1,
            shared_with=self.user2,
            created_by=self.user1
        )
        
        # Create notification
        notification = ShareNotification.objects.create(
            tenant=self.tenant,
            recipient=self.user2,
            document_share=share,
            notification_type='share_received',
            created_by=self.user1
        )
        
        # Test initial state
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.read_at)
        
        # Test mark as read
        notification.mark_as_read()
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)
    
    def test_folder_user_state(self):
        """Test folder expand/collapse state tracking"""
        folder = Folder.objects.create(
            tenant=self.tenant,
            name="Test Folder",
            created_by=self.user1
        )
        
        # Create state
        state = FolderUserState.objects.create(
            tenant=self.tenant,
            user=self.user1,
            folder=folder,
            is_expanded=True
        )
        
        self.assertTrue(state.is_expanded)
        
        # Update state
        state.is_expanded = False
        state.save()
        
        # Verify unique constraint
        with self.assertRaises(Exception):
            FolderUserState.objects.create(
                tenant=self.tenant,
                user=self.user1,
                folder=folder,
                is_expanded=True
            )