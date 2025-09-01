from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from datetime import timedelta
import boto3
import os
import tempfile
from PIL import Image
import PyPDF2
import clamd
from typing import Optional
import magic

from ..models import Document, DocumentShare
from ..storage import document_storage
from core.tenancy.models import current_tenant, Account

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def generate_thumbnail(self, document_id: str, tenant_id: str) -> bool:
    """
    Generate thumbnail for image and PDF documents.
    For PDFs, generate thumbnail from first page.
    """
    try:
        # Set tenant context
        tenant = Account.objects.get(id=tenant_id)
        current_tenant.set(tenant)
        
        document = Document.objects.get(id=document_id, tenant_id=tenant_id)
        
        # Only process images and PDFs
        if document.file_type not in ['image', 'pdf']:
            logger.info(f"Skipping thumbnail for {document.file_type} document {document_id}")
            return True
        
        # Download file from S3 to temp location
        s3_client = boto3.client('s3')
        with tempfile.NamedTemporaryFile(suffix=document.file_extension, delete=False) as tmp_file:
            s3_client.download_file(
                document.s3_bucket,
                document.s3_key,
                tmp_file.name
            )
            
            # Generate thumbnail
            thumbnail_path = tmp_file.name + '_thumb.jpg'
            
            if document.file_type == 'image':
                # Generate image thumbnail
                with Image.open(tmp_file.name) as img:
                    img.thumbnail((200, 200))
                    img.save(thumbnail_path, 'JPEG', quality=85)
            
            elif document.file_type == 'pdf':
                # Generate PDF thumbnail from first page
                # This requires pdf2image library
                from pdf2image import convert_from_path
                images = convert_from_path(tmp_file.name, first_page=1, last_page=1)
                if images:
                    images[0].thumbnail((200, 200))
                    images[0].save(thumbnail_path, 'JPEG', quality=85)
            
            # Upload thumbnail to S3
            if os.path.exists(thumbnail_path):
                thumbnail_key = document_storage.generate_thumbnail_key(document.s3_key)
                
                with open(thumbnail_path, 'rb') as thumb_file:
                    s3_client.upload_file(
                        thumb_file,
                        document.s3_bucket,
                        thumbnail_key,
                        ExtraArgs={'ContentType': 'image/jpeg'}
                    )
                
                # Update document with thumbnail key
                document.thumbnail_s3_key = thumbnail_key
                document.save(update_fields=['thumbnail_s3_key'])
                
                logger.info(f"Generated thumbnail for document {document_id}")
                
                # Cleanup temp files
                os.unlink(tmp_file.name)
                os.unlink(thumbnail_path)
                
                return True
    
    except Exception as e:
        logger.error(f"Failed to generate thumbnail for document {document_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    
    finally:
        current_tenant.set(None)


@shared_task(bind=True, max_retries=3)
def scan_document_for_viruses(self, document_id: str, tenant_id: str) -> bool:
    """
    Scan uploaded document for viruses using ClamAV.
    """
    try:
        # Set tenant context
        tenant = Account.objects.get(id=tenant_id)
        current_tenant.set(tenant)
        
        document = Document.objects.get(id=document_id, tenant_id=tenant_id)
        
        # Download file from S3
        s3_client = boto3.client('s3')
        with tempfile.NamedTemporaryFile(suffix=document.file_extension, delete=False) as tmp_file:
            s3_client.download_file(
                document.s3_bucket,
                document.s3_key,
                tmp_file.name
            )
            
            # Scan with ClamAV
            try:
                cd = clamd.ClamdUnixSocket()
                scan_result = cd.scan(tmp_file.name)
                
                if scan_result and tmp_file.name in scan_result:
                    status, virus_name = scan_result[tmp_file.name]
                    
                    if status == 'FOUND':
                        # Virus detected - quarantine document
                        logger.warning(f"Virus detected in document {document_id}: {virus_name}")
                        
                        document.is_quarantined = True
                        document.quarantine_reason = f"Virus detected: {virus_name}"
                        document.save(update_fields=['is_quarantined', 'quarantine_reason'])
                        
                        # Delete from S3
                        document_storage.delete_file(document.s3_key)
                        
                        # TODO: Send notification to user and admin
                        
                        return False
                    
            except Exception as e:
                logger.warning(f"ClamAV not available, skipping virus scan: {str(e)}")
            
            # Clean file - mark as scanned
            document.virus_scanned = True
            document.virus_scanned_at = timezone.now()
            document.save(update_fields=['virus_scanned', 'virus_scanned_at'])
            
            # Cleanup
            os.unlink(tmp_file.name)
            
            logger.info(f"Document {document_id} passed virus scan")
            return True
    
    except Exception as e:
        logger.error(f"Failed to scan document {document_id}: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    
    finally:
        current_tenant.set(None)


@shared_task(bind=True)
def extract_document_text(self, document_id: str, tenant_id: str) -> bool:
    """
    Extract text content from documents for search indexing.
    """
    try:
        # Set tenant context
        tenant = Account.objects.get(id=tenant_id)
        current_tenant.set(tenant)
        
        document = Document.objects.get(id=document_id, tenant_id=tenant_id)
        
        # Only process text-based documents
        if document.file_type not in ['pdf', 'word', 'text']:
            return True
        
        # Download file from S3
        s3_client = boto3.client('s3')
        with tempfile.NamedTemporaryFile(suffix=document.file_extension, delete=False) as tmp_file:
            s3_client.download_file(
                document.s3_bucket,
                document.s3_key,
                tmp_file.name
            )
            
            extracted_text = ""
            
            if document.file_type == 'pdf':
                # Extract text from PDF
                with open(tmp_file.name, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        extracted_text += page.extract_text() + "\n"
            
            elif document.file_type == 'text':
                # Read text file
                with open(tmp_file.name, 'r', encoding='utf-8', errors='ignore') as text_file:
                    extracted_text = text_file.read()
            
            elif document.file_type == 'word':
                # Extract text from Word document
                from docx import Document as DocxDocument
                doc = DocxDocument(tmp_file.name)
                for paragraph in doc.paragraphs:
                    extracted_text += paragraph.text + "\n"
            
            # Update document with extracted text for search
            if extracted_text:
                document.extracted_text = extracted_text[:10000]  # Limit to 10k chars
                document.search_vector = f"{document.original_name} {document.nickname} {document.description} {extracted_text[:1000]}".lower()
                document.text_extracted = True
                document.text_extracted_at = timezone.now()
                document.save(update_fields=['extracted_text', 'search_vector', 'text_extracted', 'text_extracted_at'])
            
            # Cleanup
            os.unlink(tmp_file.name)
            
            logger.info(f"Extracted text from document {document_id}")
            return True
    
    except Exception as e:
        logger.error(f"Failed to extract text from document {document_id}: {str(e)}")
        return False
    
    finally:
        current_tenant.set(None)


@shared_task
def process_uploaded_document(document_id: str, tenant_id: str) -> None:
    """
    Main task to process newly uploaded documents.
    Chains multiple processing tasks.
    """
    logger.info(f"Processing uploaded document {document_id}")
    
    # Chain tasks
    (
        scan_document_for_viruses.si(document_id, tenant_id) |
        generate_thumbnail.si(document_id, tenant_id) |
        extract_document_text.si(document_id, tenant_id)
    ).apply_async()


@shared_task
def cleanup_expired_shares() -> int:
    """
    Periodic task to cleanup expired document shares.
    Run daily via Celery beat.
    """
    try:
        expired_shares = DocumentShare.objects.filter(
            expires_at__lt=timezone.now(),
            status='pending'
        )
        
        count = expired_shares.count()
        
        for share in expired_shares:
            share.status = 'expired'
            share.save(update_fields=['status'])
            
            # TODO: Send notification about expired share
        
        logger.info(f"Cleaned up {count} expired document shares")
        return count
    
    except Exception as e:
        logger.error(f"Failed to cleanup expired shares: {str(e)}")
        return 0


@shared_task
def generate_document_report(tenant_id: str, start_date: str, end_date: str) -> str:
    """
    Generate document usage report for a tenant.
    """
    try:
        # Set tenant context
        tenant = Account.objects.get(id=tenant_id)
        current_tenant.set(tenant)
        
        # Query documents within date range
        documents = Document.objects.filter(
            tenant_id=tenant_id,
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Generate report data
        report_data = {
            'tenant': tenant.name,
            'period': f"{start_date} to {end_date}",
            'total_documents': documents.count(),
            'total_size': sum(d.file_size for d in documents),
            'by_type': {},
            'by_user': {},
            'shares': DocumentShare.objects.filter(
                tenant_id=tenant_id,
                shared_at__gte=start_date,
                shared_at__lte=end_date
            ).count()
        }
        
        # Group by file type
        for file_type in ['word', 'excel', 'pdf', 'image', 'csv', 'text', 'generic']:
            count = documents.filter(file_type=file_type).count()
            if count > 0:
                report_data['by_type'][file_type] = count
        
        # TODO: Generate PDF or Excel report
        # TODO: Upload to S3 and send notification
        
        logger.info(f"Generated document report for tenant {tenant_id}")
        return str(report_data)
    
    except Exception as e:
        logger.error(f"Failed to generate report: {str(e)}")
        raise
    
    finally:
        current_tenant.set(None)