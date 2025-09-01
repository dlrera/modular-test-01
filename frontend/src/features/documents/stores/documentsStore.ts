/**
 * Document Management Store
 * 
 * Centralized state management for the document management module using Pinia.
 * Handles all document, folder, sharing, and notification operations.
 * 
 * @module documentsStore
 * @author Development Team
 * @date December 2024
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Document, Folder, DocumentShare, ShareNotification, UploadFormData, SearchParams } from '../types'
import { documentsApi } from '../services/documentsApi'

export const useDocumentsStore = defineStore('documents', () => {
  // State
  const documents = ref<Document[]>([])
  const folders = ref<Folder[]>([])
  const shares = ref<DocumentShare[]>([])
  const notifications = ref<ShareNotification[]>([])
  const currentFolder = ref<string | null>(null)
  const loading = ref(false)
  const searchQuery = ref('')
  const selectedDocuments = ref<string[]>([])
  const sortBy = ref<'name' | 'date' | 'size'>('name')
  const showArchived = ref(false)

  // Computed
  const sortedDocuments = computed(() => {
    let docs = [...documents.value]
    
    // Filter by current folder
    if (currentFolder.value) {
      docs = docs.filter(d => d.folder === currentFolder.value)
    } else {
      docs = docs.filter(d => !d.folder)
    }
    
    // Filter by archived status
    docs = docs.filter(d => d.isArchived === showArchived.value)
    
    // Sort
    switch (sortBy.value) {
      case 'date':
        docs.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
        break
      case 'size':
        docs.sort((a, b) => b.fileSize - a.fileSize)
        break
      default:
        docs.sort((a, b) => a.displayName.localeCompare(b.displayName))
    }
    
    return docs
  })

  const currentFolderPath = computed(() => {
    if (!currentFolder.value) return '/'
    const folder = folders.value.find(f => f.id === currentFolder.value)
    return folder?.fullPath || '/'
  })

  const unreadNotificationCount = computed(() => {
    return notifications.value.filter(n => !n.isRead).length
  })

  const folderTree = computed(() => {
    // Build hierarchical tree from flat folders list
    const rootFolders = folders.value.filter(f => !f.parent)
    
    const buildTree = (parent: Folder): Folder => {
      const children = folders.value.filter(f => f.parent === parent.id)
      return {
        ...parent,
        children: children.map(child => buildTree(child))
      }
    }
    
    return rootFolders.map(folder => buildTree(folder))
  })

  // Actions
  async function fetchAllDocuments() {
    loading.value = true
    try {
      console.log('Fetching ALL documents from API...')
      const response = await documentsApi.listDocuments({
        // Don't filter by folder to get all documents
        archived: showArchived.value,
        sort: sortBy.value
      })
      console.log('All documents API response:', response)
      
      // Handle paginated response
      if (response.data.results) {
        documents.value = response.data.results
        console.log('Set all documents (paginated):', response.data.results)
      } else if (Array.isArray(response.data)) {
        documents.value = response.data
        console.log('Set all documents (array):', response.data)
      } else {
        console.error('Unexpected documents response format:', response.data)
        documents.value = []
      }
    } catch (error: any) {
      console.error('Failed to fetch all documents:', error)
      if (error.response?.status === 401 || error.response?.status === 403) {
        documents.value = []
      }
    } finally {
      loading.value = false
    }
  }
  
  async function fetchDocuments() {
    loading.value = true
    try {
      console.log('Fetching documents from API...')
      const response = await documentsApi.listDocuments({
        folder: currentFolder.value,
        archived: showArchived.value,
        sort: sortBy.value
      })
      console.log('Documents API response:', response)
      
      // Handle paginated response
      if (response.data.results) {
        documents.value = response.data.results
        console.log('Set documents (paginated):', response.data.results)
      } else if (Array.isArray(response.data)) {
        documents.value = response.data
        console.log('Set documents (array):', response.data)
      } else {
        console.error('Unexpected documents response format:', response.data)
        documents.value = []
      }
    } catch (error: any) {
      console.error('Failed to fetch documents:', error)
      // For development, use empty array if API fails
      if (error.response?.status === 401 || error.response?.status === 403) {
        documents.value = []
      }
    } finally {
      loading.value = false
    }
  }

  async function fetchFolders() {
    loading.value = true
    try {
      console.log('Fetching folders from API...')
      const response = await documentsApi.listFolders()
      console.log('API response:', response)
      
      // Handle paginated response
      if (response.data.results) {
        folders.value = response.data.results
        console.log('Set folders (paginated):', response.data.results)
      } else if (Array.isArray(response.data)) {
        folders.value = response.data
        console.log('Set folders (array):', response.data)
      } else {
        console.error('Unexpected response format:', response.data)
        folders.value = []
      }
    } catch (error: any) {
      console.error('Failed to fetch folders:', error)
      // For development, use empty array if API fails
      if (error.response?.status === 401 || error.response?.status === 403) {
        folders.value = []
      }
    } finally {
      loading.value = false
    }
  }

  async function uploadDocument(formData: UploadFormData) {
    try {
      console.log('Uploading document:', formData)
      const data = new FormData()
      if (formData.file) {
        data.append('file', formData.file)
      }
      if (formData.folder) {
        data.append('folder', formData.folder)
      }
      if (formData.nickname) {
        data.append('nickname', formData.nickname)
      }
      if (formData.description) {
        data.append('description', formData.description)
      }
      formData.shareWith.forEach(userId => {
        data.append('share_with', userId)
      })

      const response = await documentsApi.uploadDocument(data)
      console.log('Document uploaded:', response.data)
      documents.value.push(response.data)
      return response.data
    } catch (error: any) {
      console.error('Failed to upload document:', error)
      if (error.response?.data) {
        console.error('Error details:', error.response.data)
      }
      throw error
    }
  }

  async function createFolder(name: string, parentId: string | null = null) {
    try {
      console.log('Creating folder:', { name, parentId })
      const response = await documentsApi.createFolder({
        name,
        parent: parentId
      })
      console.log('Folder created:', response.data)
      folders.value.push(response.data)
      return response.data
    } catch (error: any) {
      console.error('Failed to create folder:', error)
      // For development, show what went wrong
      if (error.response?.data) {
        console.error('Error details:', error.response.data)
      }
      throw error
    }
  }

  async function toggleFolderExpanded(folderId: string) {
    const folder = folders.value.find(f => f.id === folderId)
    if (folder) {
      const response = await documentsApi.toggleFolderExpand(folderId)
      folder.isExpanded = response.data.is_expanded
    }
  }

  async function archiveDocument(documentId: string) {
    await documentsApi.archiveDocument(documentId)
    const doc = documents.value.find(d => d.id === documentId)
    if (doc) {
      doc.isArchived = true
      doc.archivedAt = new Date().toISOString()
    }
  }

  async function restoreDocument(documentId: string) {
    await documentsApi.restoreDocument(documentId)
    const doc = documents.value.find(d => d.id === documentId)
    if (doc) {
      doc.isArchived = false
      doc.archivedAt = null
    }
  }

  async function deleteDocument(documentId: string) {
    await documentsApi.deleteDocument(documentId)
    const index = documents.value.findIndex(d => d.id === documentId)
    if (index > -1) {
      documents.value.splice(index, 1)
    }
  }

  async function shareDocument(documentId: string, userIds: string[], permissions: any) {
    const response = await documentsApi.createShare({
      document: documentId,
      shared_with: userIds,
      ...permissions
    })
    shares.value.push(response.data)
    return response.data
  }

  async function searchDocuments(params: SearchParams) {
    loading.value = true
    try {
      const response = await documentsApi.searchDocuments(params)
      return response.data
    } finally {
      loading.value = false
    }
  }

  async function fetchNotifications() {
    try {
      const response = await documentsApi.listNotifications({ is_read: false })
      // Handle paginated response
      if (response.data.results) {
        notifications.value = response.data.results
      } else if (Array.isArray(response.data)) {
        notifications.value = response.data
      } else {
        console.error('Unexpected notifications response format:', response.data)
        notifications.value = []
      }
    } catch (error: any) {
      console.error('Failed to fetch notifications:', error)
      // For development, use empty array if API fails
      if (error.response?.status === 401 || error.response?.status === 403) {
        notifications.value = []
      }
    }
  }

  async function markNotificationRead(notificationId: string) {
    await documentsApi.markNotificationRead(notificationId)
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.isRead = true
      notification.readAt = new Date().toISOString()
    }
  }

  async function acceptShare(shareId: string) {
    await documentsApi.acceptShare(shareId)
    const share = shares.value.find(s => s.id === shareId)
    if (share) {
      share.status = 'accepted'
    }
  }

  async function rejectShare(shareId: string) {
    await documentsApi.rejectShare(shareId)
    const share = shares.value.find(s => s.id === shareId)
    if (share) {
      share.status = 'rejected'
    }
  }

  return {
    // State
    documents,
    folders,
    shares,
    notifications,
    currentFolder,
    loading,
    searchQuery,
    selectedDocuments,
    sortBy,
    showArchived,
    
    // Computed
    sortedDocuments,
    currentFolderPath,
    unreadNotificationCount,
    folderTree,
    
    // Actions
    fetchDocuments,
    fetchAllDocuments,
    fetchFolders,
    uploadDocument,
    createFolder,
    toggleFolderExpanded,
    archiveDocument,
    restoreDocument,
    deleteDocument,
    shareDocument,
    searchDocuments,
    fetchNotifications,
    markNotificationRead,
    acceptShare,
    rejectShare
  }
})