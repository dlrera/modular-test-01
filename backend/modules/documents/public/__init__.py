"""
Public interfaces for the documents module.
Other modules can import and use these functions.
"""

from ..services.document_service import (
    DocumentService,
    DocumentDTO,
    SearchDocumentDTO
)


def search_documents_public(user, tenant, query: str) -> list[DocumentDTO]:
    """
    Public interface to search documents.
    Used by other modules that need to find documents.
    """
    service = DocumentService(user, tenant)
    dto = SearchDocumentDTO(query=query)
    return service.search_documents(dto)


def get_document_download_url_public(user, tenant, document_id: str) -> str:
    """
    Public interface to get a document's download URL.
    Used by other modules that need to reference documents.
    """
    from ..models import Document
    
    document = Document.objects.filter(
        id=document_id,
        tenant=tenant
    ).first()
    
    if document:
        # Check permissions
        can_access = (
            document.created_by == user or
            document.shares.filter(
                shared_with=user,
                status='accepted',
                can_download=True
            ).exists()
        )
        
        if can_access:
            return document.get_s3_url()
    
    return None