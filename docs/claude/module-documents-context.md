# Module context: documents

### Purpose
Per-tenant document repository with upload, metadata, tagging, search, and preview.

### Public interfaces (backend)
- `documents.public.upload_file(user, tenant, file, metadata) -> DocumentDTO`
- `documents.public.search(user, tenant, query, filters) -> list[DocumentDTO]`
- `documents.public.get_file_url(user, tenant, document_id) -> str`

### API endpoints (v1)
- `POST /api/v1/documents/` upload
- `GET /api/v1/documents/` list/search
- `GET /api/v1/documents/{id}` detail
- `GET /api/v1/documents/{id}/download` signed URL

### Notes
- Max 1 GB per file. Allowed: pdf, images, office, text/csv.
- Search starts with Postgres full-text + trigram. Upgrade later if needed.
- Generate thumbnails for images and lightweight PDF previews in background.