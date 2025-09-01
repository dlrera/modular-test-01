"""
Script to create test documents in the database for testing the hierarchical view
"""
import os
import sys
import django
import uuid
from datetime import datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from modules.documents.models import Document, Folder

# File type and size combinations
file_examples = [
    # Root level documents
    {"name": "Company_Overview.pdf", "folder": None, "type": "pdf", "size": 2048000},
    {"name": "README.txt", "folder": None, "type": "text", "size": 4096},
    {"name": "Budget_2024.xlsx", "folder": None, "type": "excel", "size": 1536000},
    
    # Project Documents folder files
    {"name": "Project_Charter.docx", "folder": "17368211-ad0c-4f2e-a7dd-a5eeca338e92", "type": "word", "size": 512000},
    {"name": "Timeline.xlsx", "folder": "17368211-ad0c-4f2e-a7dd-a5eeca338e92", "type": "excel", "size": 256000},
    {"name": "Stakeholders.csv", "folder": "17368211-ad0c-4f2e-a7dd-a5eeca338e92", "type": "csv", "size": 32000},
    
    # Contracts subfolder files
    {"name": "Service_Agreement_2024.pdf", "folder": "95feef82-2b7b-414e-8bd6-ae381b6ca659", "type": "pdf", "size": 3072000},
    {"name": "NDA_Template.docx", "folder": "95feef82-2b7b-414e-8bd6-ae381b6ca659", "type": "word", "size": 128000},
    {"name": "Vendor_Contract_ABC.pdf", "folder": "95feef82-2b7b-414e-8bd6-ae381b6ca659", "type": "pdf", "size": 2560000},
    {"name": "Amendment_01.docx", "folder": "95feef82-2b7b-414e-8bd6-ae381b6ca659", "type": "word", "size": 96000},
    
    # Reports subfolder files
    {"name": "Q1_Financial_Report.xlsx", "folder": "fcfddaac-c210-4982-bde0-f265a5b11501", "type": "excel", "size": 4096000},
    {"name": "Q2_Financial_Report.xlsx", "folder": "fcfddaac-c210-4982-bde0-f265a5b11501", "type": "excel", "size": 4256000},
    {"name": "Annual_Summary_2023.pdf", "folder": "fcfddaac-c210-4982-bde0-f265a5b11501", "type": "pdf", "size": 5120000},
    {"name": "Performance_Metrics.csv", "folder": "fcfddaac-c210-4982-bde0-f265a5b11501", "type": "csv", "size": 128000},
    
    # Test Folder files
    {"name": "Test_Document_1.txt", "folder": "99497d85-c44c-4bf5-99c6-fdefd913895a", "type": "text", "size": 1024},
    {"name": "Test_Image.png", "folder": "99497d85-c44c-4bf5-99c6-fdefd913895a", "type": "image", "size": 2048000},
]

def get_mime_type(file_type):
    """Get MIME type based on file type"""
    mime_types = {
        'pdf': 'application/pdf',
        'word': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text': 'text/plain',
        'csv': 'text/csv',
        'image': 'image/png',
        'generic': 'application/octet-stream'
    }
    return mime_types.get(file_type, 'application/octet-stream')

def get_file_extension(filename):
    """Extract file extension from filename"""
    return '.' + filename.split('.')[-1] if '.' in filename else ''

def create_documents():
    """Create test documents in the database"""
    created_count = 0
    
    # Use hard-coded tenant_id for testing
    tenant_id = 1
    
    for file_data in file_examples:
        try:
            # Check if folder exists
            folder = None
            if file_data['folder']:
                try:
                    folder = Folder.objects.get(id=file_data['folder'])
                except Folder.DoesNotExist:
                    print(f"Folder {file_data['folder']} not found, creating document at root")
                    folder = None
            
            # Create nickname from filename
            nickname = file_data['name'].replace('_', ' ').replace('.', ' ').split()[0]
            
            # Create document
            doc = Document.objects.create(
                id=uuid.uuid4(),
                tenant_id=tenant_id,  # Use tenant_id directly
                folder=folder,
                original_name=file_data['name'],
                nickname=f"{nickname} Document",
                description=f"Test document: {file_data['name']}",
                file_type=file_data['type'],
                mime_type=get_mime_type(file_data['type']),
                file_size=file_data['size'],
                file_extension=get_file_extension(file_data['name']),
                # S3 storage fields
                s3_bucket='test-bucket',
                s3_key=f"test/documents/{uuid.uuid4()}/{file_data['name']}",
                s3_version_id='v1',
                # Remove fields that don't exist: file_hash, s3_etag
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            
            print(f"Created: {doc.nickname} in {folder.name if folder else 'root'}")
            created_count += 1
            
        except Exception as e:
            print(f"Error creating {file_data['name']}: {e}")
    
    print(f"\nTotal documents created: {created_count}")

def create_nested_folders():
    """Create some nested folders for deeper hierarchy"""
    # Use hard-coded tenant_id for testing
    tenant_id = 1
    
    try:
        # Create 2024 subfolder under Contracts
        folder_2024 = Folder.objects.create(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name="2024",
            parent_id="95feef82-2b7b-414e-8bd6-ae381b6ca659"  # Contracts folder
        )
        print(f"Created nested folder: 2024 under Contracts")
        
        # Create Q1 subfolder under 2024
        folder_q1 = Folder.objects.create(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name="Q1",
            parent=folder_2024
        )
        print(f"Created nested folder: Q1 under 2024")
        
        # Add a document to the deeply nested folder
        Document.objects.create(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            folder=folder_q1,
            original_name="Q1_Contract_Review.pdf",
            nickname="Q1 Contract Review",
            description="Quarterly contract review document",
            file_type='pdf',
            mime_type='application/pdf',
            file_size=1024000,
            file_extension='.pdf',
            s3_bucket='test-bucket',
            s3_key=f"test/documents/{uuid.uuid4()}/Q1_Contract_Review.pdf",
            s3_version_id='v1'
        )
        print(f"Created document in deeply nested folder: Q1")
        
        # Create Archive folder at root
        archive_folder = Folder.objects.create(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name="Archive",
            parent=None
        )
        print(f"Created folder: Archive at root")
        
        # Create 2023 subfolder under Archive
        folder_2023 = Folder.objects.create(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name="2023",
            parent=archive_folder
        )
        print(f"Created nested folder: 2023 under Archive")
        
        # Add some old documents to archive
        Document.objects.create(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            folder=folder_2023,
            original_name="2023_Year_End_Report.pdf",
            nickname="2023 Year End Report",
            description="Archived year-end report for 2023",
            file_type='pdf',
            mime_type='application/pdf',
            file_size=8192000,
            file_extension='.pdf',
            s3_bucket='test-bucket',
            s3_key=f"test/documents/{uuid.uuid4()}/2023_Year_End_Report.pdf",
            s3_version_id='v1'
        )
        print(f"Created archived document in 2023 folder")
        
    except Exception as e:
        print(f"Error creating nested folders: {e}")

if __name__ == "__main__":
    print("Creating test documents and folders...\n")
    create_nested_folders()
    create_documents()
    print("\nDone! Refresh your browser to see the hierarchical structure.")