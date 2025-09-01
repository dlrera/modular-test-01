import api from '@/services/api'
import type { Document, Folder, DocumentShare, ShareNotification } from '../types'

const API_BASE = '/api/v1'

export const documentsApi = {
  // Folders
  async listFolders(params?: { parent?: string }) {
    return api.get<Folder[]>(`${API_BASE}/folders/`, { params })
  },

  async createFolder(data: { name: string; parent?: string | null }) {
    return api.post<Folder>(`${API_BASE}/folders/`, data)
  },

  async toggleFolderExpand(folderId: string) {
    return api.post<{ is_expanded: boolean }>(`${API_BASE}/folders/${folderId}/toggle_expand/`)
  },

  async getFolderTree() {
    return api.get<Folder[]>(`${API_BASE}/folders/tree/`)
  },

  // Documents
  async listDocuments(params?: { folder?: string | null; archived?: boolean; sort?: string }) {
    return api.get<Document[]>(`${API_BASE}/files/`, { params })
  },

  async uploadDocument(data: FormData) {
    return api.post<Document>(`${API_BASE}/files/upload/`, data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  async getDocument(documentId: string) {
    return api.get<Document>(`${API_BASE}/files/${documentId}/`)
  },

  async updateDocument(documentId: string, data: Partial<Document>) {
    return api.patch<Document>(`${API_BASE}/files/${documentId}/`, data)
  },

  async deleteDocument(documentId: string) {
    return api.delete(`${API_BASE}/files/${documentId}/`)
  },

  async archiveDocument(documentId: string) {
    return api.post(`${API_BASE}/files/${documentId}/archive/`)
  },

  async restoreDocument(documentId: string) {
    return api.post(`${API_BASE}/files/${documentId}/restore/`)
  },

  async getDownloadUrl(documentId: string) {
    return api.get<{ download_url: string }>(`${API_BASE}/files/${documentId}/download_url/`)
  },

  async searchDocuments(params: {
    query: string
    includeDescription?: boolean
    folder?: string | null
    fileTypes?: string[]
    archived?: boolean
  }) {
    return api.post<Document[]>(`${API_BASE}/files/search/`, params)
  },

  // Shares
  async listShares(params?: { type?: 'sent' | 'received'; status?: string }) {
    return api.get<DocumentShare[]>(`${API_BASE}/shares/`, { params })
  },

  async createShare(data: {
    document: string
    shared_with: string[]
    can_download?: boolean
    can_share?: boolean
    can_edit?: boolean
    message?: string
  }) {
    return api.post<DocumentShare>(`${API_BASE}/shares/`, data)
  },

  async acceptShare(shareId: string) {
    return api.post(`${API_BASE}/shares/${shareId}/accept/`)
  },

  async rejectShare(shareId: string) {
    return api.post(`${API_BASE}/shares/${shareId}/reject/`)
  },

  async revokeShare(shareId: string) {
    return api.post(`${API_BASE}/shares/${shareId}/revoke/`)
  },

  // Notifications
  async listNotifications(params?: { is_read?: boolean }) {
    return api.get<ShareNotification[]>(`${API_BASE}/notifications/`, { params })
  },

  async markNotificationRead(notificationId: string) {
    return api.post(`${API_BASE}/notifications/${notificationId}/mark_read/`)
  },

  async markAllNotificationsRead() {
    return api.post<{ marked_read: number }>(`${API_BASE}/notifications/mark_all_read/`)
  },

  async getUnreadCount() {
    return api.get<{ unread_count: number }>(`${API_BASE}/notifications/unread_count/`)
  }
}