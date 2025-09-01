import axios from 'axios'
import type { Document, Folder, DocumentShare, ShareNotification } from '../types'

const API_BASE = '/api/v1'

export const documentsApi = {
  // Folders
  async listFolders(params?: { parent?: string }) {
    return axios.get<Folder[]>(`${API_BASE}/folders/`, { params })
  },

  async createFolder(data: { name: string; parent?: string | null }) {
    return axios.post<Folder>(`${API_BASE}/folders/`, data)
  },

  async toggleFolderExpand(folderId: string) {
    return axios.post<{ is_expanded: boolean }>(`${API_BASE}/folders/${folderId}/toggle_expand/`)
  },

  async getFolderTree() {
    return axios.get<Folder[]>(`${API_BASE}/folders/tree/`)
  },

  // Documents
  async listDocuments(params?: { folder?: string | null; archived?: boolean; sort?: string }) {
    return axios.get<Document[]>(`${API_BASE}/files/`, { params })
  },

  async uploadDocument(data: FormData) {
    return axios.post<Document>(`${API_BASE}/files/upload/`, data, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  async getDocument(documentId: string) {
    return axios.get<Document>(`${API_BASE}/files/${documentId}/`)
  },

  async updateDocument(documentId: string, data: Partial<Document>) {
    return axios.patch<Document>(`${API_BASE}/files/${documentId}/`, data)
  },

  async deleteDocument(documentId: string) {
    return axios.delete(`${API_BASE}/files/${documentId}/`)
  },

  async archiveDocument(documentId: string) {
    return axios.post(`${API_BASE}/files/${documentId}/archive/`)
  },

  async restoreDocument(documentId: string) {
    return axios.post(`${API_BASE}/files/${documentId}/restore/`)
  },

  async getDownloadUrl(documentId: string) {
    return axios.get<{ download_url: string }>(`${API_BASE}/files/${documentId}/download_url/`)
  },

  async searchDocuments(params: {
    query: string
    includeDescription?: boolean
    folder?: string | null
    fileTypes?: string[]
    archived?: boolean
  }) {
    return axios.post<Document[]>(`${API_BASE}/files/search/`, params)
  },

  // Shares
  async listShares(params?: { type?: 'sent' | 'received'; status?: string }) {
    return axios.get<DocumentShare[]>(`${API_BASE}/shares/`, { params })
  },

  async createShare(data: {
    document: string
    shared_with: string[]
    can_download?: boolean
    can_share?: boolean
    can_edit?: boolean
    message?: string
  }) {
    return axios.post<DocumentShare>(`${API_BASE}/shares/`, data)
  },

  async acceptShare(shareId: string) {
    return axios.post(`${API_BASE}/shares/${shareId}/accept/`)
  },

  async rejectShare(shareId: string) {
    return axios.post(`${API_BASE}/shares/${shareId}/reject/`)
  },

  async revokeShare(shareId: string) {
    return axios.post(`${API_BASE}/shares/${shareId}/revoke/`)
  },

  // Notifications
  async listNotifications(params?: { is_read?: boolean }) {
    return axios.get<ShareNotification[]>(`${API_BASE}/notifications/`, { params })
  },

  async markNotificationRead(notificationId: string) {
    return axios.post(`${API_BASE}/notifications/${notificationId}/mark_read/`)
  },

  async markAllNotificationsRead() {
    return axios.post<{ marked_read: number }>(`${API_BASE}/notifications/mark_all_read/`)
  },

  async getUnreadCount() {
    return axios.get<{ unread_count: number }>(`${API_BASE}/notifications/unread_count/`)
  }
}