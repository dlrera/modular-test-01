# Document Management Module

## Overview
This module provides comprehensive document management functionality with tenant isolation, folder organization, file sharing, and S3 storage integration.

## Original Requirements

### Core Features
1. **File Upload**
   - Users must be able to upload files into the repository.
   - Upload initiated via a button (e.g., top-right corner).
   - File upload opens a **modal** with:
     - Drag-and-drop or file picker.
     - Default file name (from the uploaded file).
     - Optional nickname field (nickname displayed instead of file name if present).
     - Description field (text).
     - Option to share file (with dropdown list of account users).
     - Author field (auto-populated with uploader's user).
     - Disabled AI parser button (future feature).

2. **Folder Structure**
   - Users can create folders and nested subfolders.
   - Folders expand/collapse with a triangle toggle.
   - Expanded/collapsed states are remembered.
   - Example: If *Folder1 > Subfolder1* is expanded, then collapsed, state persists when reopened.

3. **Sorting & Display**
   - Folders always displayed first, sorted alphabetically.
   - Files sorted alphabetically by default.
   - An **"Added" column** exists for files only; sortable.
   - No file extensions displayed.
   - Nickname (if populated) shows in the file list; otherwise, the original file name displays.

4. **File Row Options**
   - Each file row includes:
     - File type icon (Word, Excel, PDF, image, CSV, text, or generic).
     - Ability to view/edit metadata (nickname, description, share settings).
     - Option to open to view in a pop-up window (if supported).
     - Option to download file.
     - Constraints preventing upload must display as warnings.

5. **Search**
   - Search bar at top of main view.
   - Searches across file names and nicknames.
   - Optional checkbox to include file descriptions in search.

6. **Sharing**
   - File sharing available **on a file-by-file basis**.
   - Shared only with users associated with the same account.
   - There should be an interface for accepting or rejecting shared documents, with a notification icon in the document repository that when clicked allows accepting or rejecting the shared document.

### Storage
- All documents and metadata are stored in **S3**. Additional necessary metadata in RDS.

## Implementation Architecture

### Backend Components

#### Models
- `Folder` - Hierarchical folder structure with parent references
- `Document` - File metadata with S3 references
- `DocumentShare` - Sharing relationships between users
- `ShareNotification` - Pending share notifications

#### API Endpoints
- `/api/v1/documents/folders/` - Folder CRUD operations
- `/api/v1/documents/files/` - File upload and management
- `/api/v1/documents/shares/` - Share management
- `/api/v1/documents/notifications/` - Share notifications
- `/api/v1/documents/search/` - Search functionality

#### Storage
- S3 path structure: `tenants/{tenant_id}/documents/{year}/{month}/{document_id}/{filename}`
- Metadata stored in PostgreSQL with S3 references
- File content never stored in database

### Frontend Components

#### Views
- `DocumentRepository.vue` - Main document management interface
- `UploadModal.vue` - File upload with metadata
- `FolderTree.vue` - Expandable folder navigation
- `DocumentList.vue` - File listing with sorting
- `ShareNotifications.vue` - Accept/reject shared documents

#### State Management
- Pinia store for document state
- Local storage for folder expand/collapse states
- Vuex actions for CRUD operations

### Security Considerations
- Tenant isolation enforced at model level
- Pre-signed URLs for direct S3 upload/download
- File type validation and virus scanning
- Share permissions checked on every access

## Development Status

### Completed
- [x] Module structure setup
- [x] Base models with tenant isolation
- [x] S3 storage integration
- [x] Basic API endpoints
- [x] File upload functionality
- [x] Folder management
- [x] Search implementation
- [x] Sharing system

### In Progress
- [ ] Frontend components
- [ ] Notification system
- [ ] File preview functionality

### Planned
- [ ] AI parser integration
- [ ] Bulk operations
- [ ] Advanced search filters
- [ ] Activity audit log