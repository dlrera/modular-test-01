<template>
  <v-data-table
    :headers="headers"
    :items="documents"
    :loading="loading"
    item-value="id"
    class="elevation-1"
  >
    <!-- File name with icon -->
    <template v-slot:item.displayName="{ item }">
      <div class="d-flex align-center py-2">
        <v-icon :icon="getFileIcon(item.fileType)" class="mr-2" />
        <div>
          <div>{{ item.displayName }}</div>
          <div v-if="item.description" class="text-caption text-medium-emphasis">
            {{ item.description }}
          </div>
        </div>
      </div>
    </template>
    
    <!-- File size -->
    <template v-slot:item.fileSize="{ item }">
      {{ formatFileSize(item.fileSize) }}
    </template>
    
    <!-- Created date -->
    <template v-slot:item.createdAt="{ item }">
      {{ formatDate(item.createdAt) }}
    </template>
    
    <!-- Actions -->
    <template v-slot:item.actions="{ item }">
      <v-btn
        icon
        size="small"
        @click="$emit('download', item)"
        title="Download"
      >
        <v-icon size="small">mdi-download</v-icon>
      </v-btn>
      
      <v-btn
        icon
        size="small"
        @click="$emit('share', item)"
        title="Share"
      >
        <v-icon size="small">mdi-share-variant</v-icon>
      </v-btn>
      
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            size="small"
            v-bind="props"
          >
            <v-icon size="small">mdi-dots-vertical</v-icon>
          </v-btn>
        </template>
        
        <v-list density="compact">
          <v-list-item @click="$emit('edit', item)">
            <template v-slot:prepend>
              <v-icon size="small">mdi-pencil</v-icon>
            </template>
            <v-list-item-title>Edit</v-list-item-title>
          </v-list-item>
          
          <v-list-item 
            @click="$emit('archive', item)"
            v-if="!item.isArchived"
          >
            <template v-slot:prepend>
              <v-icon size="small">mdi-archive</v-icon>
            </template>
            <v-list-item-title>Archive</v-list-item-title>
          </v-list-item>
          
          <v-list-item 
            @click="$emit('restore', item)"
            v-else
          >
            <template v-slot:prepend>
              <v-icon size="small">mdi-archive-arrow-up</v-icon>
            </template>
            <v-list-item-title>Restore</v-list-item-title>
          </v-list-item>
          
          <v-divider />
          
          <v-list-item @click="$emit('delete', item)">
            <template v-slot:prepend>
              <v-icon size="small" color="error">mdi-delete</v-icon>
            </template>
            <v-list-item-title class="text-error">Delete</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
    
    <!-- No data -->
    <template v-slot:no-data>
      <div class="text-center py-8">
        <v-icon size="48" class="text-medium-emphasis mb-4">
          mdi-folder-open-outline
        </v-icon>
        <p class="text-body-1 text-medium-emphasis">
          No documents found
        </p>
      </div>
    </template>
  </v-data-table>
</template>

<script setup lang="ts">
import type { Document } from '../types'

defineProps<{
  documents: Document[]
  loading: boolean
}>()

defineEmits<{
  edit: [document: Document]
  download: [document: Document]
  share: [document: Document]
  archive: [document: Document]
  restore: [document: Document]
  delete: [document: Document]
}>()

const headers = [
  { title: 'Name', key: 'displayName', sortable: true },
  { title: 'Size', key: 'fileSize', sortable: true },
  { title: 'Added', key: 'createdAt', sortable: true },
  { title: 'Uploaded By', key: 'uploadedByName', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

function getFileIcon(fileType: string): string {
  const icons: Record<string, string> = {
    word: 'mdi-file-word',
    excel: 'mdi-file-excel',
    pdf: 'mdi-file-pdf-box',
    image: 'mdi-file-image',
    csv: 'mdi-file-delimited',
    text: 'mdi-file-document',
    generic: 'mdi-file'
  }
  return icons[fileType] || icons.generic
}

function formatFileSize(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  return `${size.toFixed(1)} ${units[unitIndex]}`
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}
</script>