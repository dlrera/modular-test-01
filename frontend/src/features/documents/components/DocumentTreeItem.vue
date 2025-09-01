<template>
  <div>
    <!-- Folder Row -->
    <v-list-item
      v-if="item.type === 'folder'"
      :style="{ paddingLeft: `${level * 24}px` }"
      @click="handleFolderClick"
      :active="item.id === selectedId"
      class="folder-item"
    >
      <template v-slot:prepend>
        <v-icon
          @click.stop="$emit('toggle', item.id)"
          class="mr-2"
        >
          {{ item.isExpanded ? 'mdi-chevron-down' : 'mdi-chevron-right' }}
        </v-icon>
        <v-icon>
          {{ item.isExpanded ? 'mdi-folder-open' : 'mdi-folder' }}
        </v-icon>
      </template>
      
      <v-list-item-title>{{ item.name }}</v-list-item-title>
      
      <template v-slot:append>
        <span class="text-caption text-medium-emphasis mr-2">
          {{ folderData.document_count || 0 }} items
        </span>
        <v-menu location="bottom end">
          <template v-slot:activator="{ props }">
            <v-btn
              icon
              variant="text"
              size="small"
              v-bind="props"
              @click.stop
            >
              <v-icon size="small">mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list density="compact">
            <v-list-item @click="$emit('create-folder', item.id)">
              <v-list-item-title>New Subfolder</v-list-item-title>
            </v-list-item>
            <v-list-item @click="handleRenameFolder">
              <v-list-item-title>Rename</v-list-item-title>
            </v-list-item>
            <v-list-item @click="handleDeleteFolder" class="text-error">
              <v-list-item-title>Delete</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-list-item>
    
    <!-- Document Row -->
    <v-list-item
      v-else
      :style="{ paddingLeft: `${(level + 1) * 24}px` }"
      @click="handleDocumentClick"
      :active="item.id === selectedId"
      class="document-item"
    >
      <template v-slot:prepend>
        <v-icon :color="getFileIconColor(documentData.file_type)">
          {{ getFileIcon(documentData.file_type) }}
        </v-icon>
      </template>
      
      <v-list-item-title>
        {{ item.name }}
        <v-chip
          v-if="documentData.isArchived"
          size="x-small"
          color="warning"
          class="ml-2"
        >
          Archived
        </v-chip>
      </v-list-item-title>
      
      <v-list-item-subtitle>
        {{ formatFileSize(documentData.file_size) }} • 
        {{ formatDate(documentData.created_at) }}
        <span v-if="documentData.uploaded_by_name">
          • By {{ documentData.uploaded_by_name }}
        </span>
      </v-list-item-subtitle>
      
      <template v-slot:append>
        <v-menu location="bottom end">
          <template v-slot:activator="{ props }">
            <v-btn
              icon
              variant="text"
              size="small"
              v-bind="props"
              @click.stop
            >
              <v-icon size="small">mdi-dots-vertical</v-icon>
            </v-btn>
          </template>
          <v-list density="compact">
            <v-list-item @click="$emit('download', documentData)">
              <template v-slot:prepend>
                <v-icon size="small">mdi-download</v-icon>
              </template>
              <v-list-item-title>Download</v-list-item-title>
            </v-list-item>
            <v-list-item @click="$emit('edit', documentData)">
              <template v-slot:prepend>
                <v-icon size="small">mdi-pencil</v-icon>
              </template>
              <v-list-item-title>Edit Details</v-list-item-title>
            </v-list-item>
            <v-list-item @click="$emit('share', documentData)">
              <template v-slot:prepend>
                <v-icon size="small">mdi-share-variant</v-icon>
              </template>
              <v-list-item-title>Share</v-list-item-title>
            </v-list-item>
            <v-divider />
            <v-list-item 
              v-if="!documentData.isArchived"
              @click="$emit('archive', documentData)"
            >
              <template v-slot:prepend>
                <v-icon size="small">mdi-archive</v-icon>
              </template>
              <v-list-item-title>Archive</v-list-item-title>
            </v-list-item>
            <v-list-item 
              @click="$emit('delete', documentData)" 
              class="text-error"
            >
              <template v-slot:prepend>
                <v-icon size="small">mdi-delete</v-icon>
              </template>
              <v-list-item-title>Delete</v-list-item-title>
            </v-list-item>
          </v-list>
        </v-menu>
      </template>
    </v-list-item>
    
    <!-- Render children if folder is expanded -->
    <template v-if="item.type === 'folder' && item.isExpanded && item.children">
      <DocumentTreeItem
        v-for="child in item.children"
        :key="child.id"
        :item="child"
        :level="level + 1"
        :selected-id="selectedId"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
        @edit="$emit('edit', $event)"
        @download="$emit('download', $event)"
        @share="$emit('share', $event)"
        @archive="$emit('archive', $event)"
        @delete="$emit('delete', $event)"
        @create-folder="$emit('create-folder', $event)"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Document, Folder } from '../types'

interface TreeItem {
  id: string
  type: 'folder' | 'document'
  name: string
  data: Folder | Document
  children?: TreeItem[]
  isExpanded?: boolean
}

const props = defineProps<{
  item: TreeItem
  level: number
  selectedId?: string | null
}>()

const emit = defineEmits<{
  select: [item: TreeItem]
  toggle: [folderId: string]
  edit: [document: Document]
  download: [document: Document]
  share: [document: Document]
  archive: [document: Document]
  delete: [document: Document]
  'create-folder': [parentId: string | null]
}>()

const folderData = computed(() => props.item.data as Folder)
const documentData = computed(() => props.item.data as Document)

function handleFolderClick() {
  emit('select', props.item)
}

function handleDocumentClick() {
  emit('select', props.item)
}

function handleRenameFolder() {
  // TODO: Implement folder rename
  console.log('Rename folder:', props.item.name)
}

function handleDeleteFolder() {
  // TODO: Implement folder delete
  console.log('Delete folder:', props.item.name)
}

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

function getFileIconColor(fileType: string): string {
  const colors: Record<string, string> = {
    word: 'blue',
    excel: 'green',
    pdf: 'red',
    image: 'orange',
    csv: 'teal',
    text: 'grey',
    generic: 'grey'
  }
  return colors[fileType] || colors.generic
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(date)
}
</script>

<style scoped>
.folder-item {
  font-weight: 500;
}

.document-item {
  border-left: 2px solid transparent;
}

.document-item:hover {
  border-left-color: rgb(var(--v-theme-primary));
}
</style>