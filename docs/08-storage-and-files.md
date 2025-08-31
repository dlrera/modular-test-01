# Storage and files

- Provider: AWS S3. Local dev uses MinIO.
- Max upload size: 1 GB (configurable).
- Allowed types: PDF, images, Office docs, text/CSV.
- Key format: `tenants/{tenant_id}/{module}/{yyyy}/{mm}/{uuid-filename}`.
- Never mix tenant files under the same prefix.
- Thumbnails and previews stored under a `previews/` subpath. Generate image thumbnails and first-page PDF previews in background tasks.