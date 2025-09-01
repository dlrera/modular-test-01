<template>
  <v-container fluid>
    <!-- Page Header -->
    <v-row class="mb-3">
      <v-col cols="12" md="8">
        <h1 class="text-h5 font-weight-medium mb-1">
          Document Management
        </h1>
        <p class="text-body-2 text-medium-emphasis">
          Upload, organize, and share documents with your team
        </p>
      </v-col>
      <v-col cols="12" md="4" class="text-md-right">
        <v-btn 
          color="primary" 
          prepend-icon="mdi-plus"
          @click="showUploadDialog = true"
        >
          Upload Document
        </v-btn>
      </v-col>
    </v-row>

    <!-- Search Bar -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-text-field
          v-model="searchQuery"
          variant="outlined"
          density="compact"
          placeholder="Search documents..."
          prepend-inner-icon="mdi-magnify"
          clearable
          @update:model-value="handleSearch"
        >
          <template v-slot:append>
            <v-checkbox
              v-model="includeDescription"
              label="Include descriptions"
              density="compact"
              hide-details
              class="mt-0"
            />
          </template>
        </v-text-field>
      </v-col>
      <v-col cols="12" md="6" class="text-md-right">
        <!-- Notifications -->
        <v-badge
          :content="store.unreadNotificationCount"
          :model-value="store.unreadNotificationCount > 0"
          color="error"
          class="mr-4"
        >
          <v-btn
            icon
            @click="showNotifications = true"
          >
            <v-icon>mdi-bell</v-icon>
          </v-btn>
        </v-badge>

        <!-- View Options -->
        <v-btn-toggle
          v-model="sortBy"
          mandatory
          density="compact"
          divided
          variant="outlined"
        >
          <v-btn value="name" size="small">
            <v-icon size="small">mdi-sort-alphabetical-ascending</v-icon>
            Name
          </v-btn>
          <v-btn value="date" size="small">
            <v-icon size="small">mdi-calendar</v-icon>
            Added
          </v-btn>
          <v-btn value="size" size="small">
            <v-icon size="small">mdi-database</v-icon>
            Size
          </v-btn>
        </v-btn-toggle>
      </v-col>
    </v-row>

    <!-- Main Content Area - Unified Tree View -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex align-center">
            <v-icon class="mr-2">mdi-folder-home</v-icon>
            <span>{{ currentPath }}</span>
            <v-spacer />
            <v-btn
              color="primary"
              size="small"
              prepend-icon="mdi-folder-plus"
              @click="showCreateFolderDialog = true"
              class="mr-2"
            >
              New Folder
            </v-btn>
            <v-btn
              color="primary"
              size="small"
              prepend-icon="mdi-file-plus"
              @click="showUploadDialog = true"
            >
              Upload File
            </v-btn>
          </v-card-title>
          <v-divider />
          <v-card-text class="pa-0">
            <DocumentTree
              :folders="store.folders"
              :documents="store.documents"
              :selected-id="selectedItemId"
              @select="handleItemSelect"
              @toggle="handleToggleFolderExpanded"
              @edit="handleEditDocument"
              @download="handleDownloadDocument"
              @share="handleShareDocument"
              @archive="handleArchiveDocument"
              @delete="handleDeleteDocument"
              @create-folder="handleCreateSubfolder"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Upload Dialog -->
    <UploadModal
      v-model="showUploadDialog"
      :current-folder="store.currentFolder"
      @upload="handleUpload"
    />

    <!-- Create Folder Dialog -->
    <CreateFolderDialog
      v-model="showCreateFolderDialog"
      :parent-folder="store.currentFolder"
      @create="handleCreateFolder"
    />

    <!-- Share Dialog -->
    <ShareDialog
      v-model="showShareDialog"
      :document="selectedDocument"
      @share="handleShare"
    />

    <!-- Notifications Panel -->
    <NotificationsPanel
      v-model="showNotifications"
      :notifications="store.notifications"
      @accept="store.acceptShare"
      @reject="store.rejectShare"
      @mark-read="store.markNotificationRead"
    />
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useDocumentsStore } from '../stores/documentsStore'
import { documentsApi } from '../services/documentsApi'
import DocumentTree from './DocumentTree.vue'
import UploadModal from './UploadModal.vue'
import CreateFolderDialog from './CreateFolderDialog.vue'
import ShareDialog from './ShareDialog.vue'
import NotificationsPanel from './NotificationsPanel.vue'
import type { Document, UploadFormData } from '../types'

// Simple debounce implementation
function debounce(fn: Function, delay: number) {
  let timeoutId: NodeJS.Timeout
  return function (...args: any[]) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

const store = useDocumentsStore()

// Reactive state
const showUploadDialog = ref(false)
const showCreateFolderDialog = ref(false)
const showShareDialog = ref(false)
const showNotifications = ref(false)
const selectedDocument = ref<Document | null>(null)
const selectedItemId = ref<string | null>(null)
const searchQuery = ref('')
const includeDescription = ref(false)
const sortBy = ref<'name' | 'date' | 'size'>('name')

// Computed
const currentPath = computed(() => {
  if (!store.currentFolder) return 'All Documents'
  const folder = store.folders.find(f => f.id === store.currentFolder)
  return folder?.full_path || 'All Documents'
})

// Initialize
onMounted(async () => {
  console.log('DocumentRepository mounted, fetching data...')
  try {
    await Promise.all([
      store.fetchFolders(),
      store.fetchAllDocuments(),  // Fetch ALL documents for the tree view
      store.fetchNotifications()
    ])
    console.log('Data fetched:', {
      folders: store.folders,
      documents: store.documents,
      notifications: store.notifications
    })
  } catch (error) {
    console.error('Error fetching initial data:', error)
  }
})

// Watch for sort changes
watch(sortBy, (value) => {
  store.sortBy = value
})

// Handlers
const handleSearch = debounce(async () => {
  if (searchQuery.value) {
    await store.searchDocuments({
      query: searchQuery.value,
      includeDescription: includeDescription.value,
      folder: store.currentFolder,
      fileTypes: [],
      archived: store.showArchived
    })
  } else {
    await store.fetchDocuments()
  }
}, 300)

function handleItemSelect(item: any) {
  selectedItemId.value = item.id
  if (item.type === 'folder') {
    store.currentFolder = item.id
    store.fetchDocuments()
  }
}

async function handleToggleFolderExpanded(folderId: string) {
  await store.toggleFolderExpanded(folderId)
  // Refresh folders to get updated expansion state
  await store.fetchFolders()
}

function handleCreateSubfolder(parentId: string | null) {
  store.currentFolder = parentId
  showCreateFolderDialog.value = true
}

async function handleUpload(formData: UploadFormData) {
  await store.uploadDocument(formData)
  showUploadDialog.value = false
}

async function handleCreateFolder(name: string) {
  await store.createFolder(name, store.currentFolder)
  showCreateFolderDialog.value = false
}

function handleEditDocument(document: Document) {
  // Open edit dialog
  selectedDocument.value = document
}

async function handleDownloadDocument(document: Document) {
  const response = await documentsApi.getDownloadUrl(document.id)
  window.open(response.data.download_url, '_blank')
}

function handleShareDocument(document: Document) {
  selectedDocument.value = document
  showShareDialog.value = true
}

async function handleShare(userIds: string[], permissions: any) {
  if (selectedDocument.value) {
    await store.shareDocument(selectedDocument.value.id, userIds, permissions)
    showShareDialog.value = false
  }
}

async function handleArchiveDocument(document: Document) {
  await store.archiveDocument(document.id)
}

async function handleDeleteDocument(document: Document) {
  if (confirm(`Are you sure you want to delete "${document.displayName}"?`)) {
    await store.deleteDocument(document.id)
  }
}
</script>