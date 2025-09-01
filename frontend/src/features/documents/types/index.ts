export interface Folder {
  id: string
  name: string
  parent: string | null
  children: Folder[]
  documentCount: number
  fullPath: string
  isExpanded: boolean
  createdAt: string
  updatedAt: string
}

export interface Document {
  id: string
  folder: string | null
  originalName: string
  nickname: string
  displayName: string
  description: string
  fileType: 'word' | 'excel' | 'pdf' | 'image' | 'csv' | 'text' | 'generic'
  mimeType: string
  fileSize: number
  fileExtension: string
  downloadUrl: string
  folderPath: string
  uploadedByName: string
  shares: DocumentShare[]
  canShare: boolean
  isArchived: boolean
  archivedAt: string | null
  aiProcessed: boolean
  createdAt: string
  updatedAt: string
}

export interface DocumentShare {
  id: string
  document: string
  documentName: string
  sharedBy: string
  sharedByName: string
  sharedWith: string
  sharedWithName: string
  status: 'pending' | 'accepted' | 'rejected' | 'revoked'
  canDownload: boolean
  canShare: boolean
  canEdit: boolean
  message: string
  sharedAt: string
  respondedAt: string | null
  expiresAt: string | null
}

export interface ShareNotification {
  id: string
  documentShare: string
  documentName: string
  sharedByName: string
  notificationType: 'share_received' | 'share_accepted' | 'share_rejected' | 'share_revoked'
  shareStatus: string
  isRead: boolean
  readAt: string | null
  createdAt: string
}

export interface UploadFormData {
  file: File | null
  folder: string | null
  nickname: string
  description: string
  shareWith: string[]
}

export interface SearchParams {
  query: string
  includeDescription: boolean
  folder: string | null
  fileTypes: string[]
  archived: boolean
}

export interface User {
  id: string
  username: string
  email: string
  fullName: string
}