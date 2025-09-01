<template>
  <v-list density="compact" class="pa-0">
    <!-- Root level items -->
    <template v-for="item in treeItems" :key="item.id">
      <DocumentTreeItem
        :item="item"
        :level="0"
        :selected-id="selectedId"
        @select="handleSelect"
        @toggle="handleToggle"
        @edit="$emit('edit', $event)"
        @download="$emit('download', $event)"
        @share="$emit('share', $event)"
        @archive="$emit('archive', $event)"
        @delete="$emit('delete', $event)"
        @create-folder="$emit('create-folder', $event)"
      />
    </template>
  </v-list>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Document, Folder } from '../types'
import DocumentTreeItem from './DocumentTreeItem.vue'

interface TreeItem {
  id: string
  type: 'folder' | 'document'
  name: string
  data: Folder | Document
  children?: TreeItem[]
  isExpanded?: boolean
}

const props = defineProps<{
  folders: Folder[]
  documents: Document[]
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

// Build hierarchical tree structure
const treeItems = computed(() => {
  const items: TreeItem[] = []
  const folderMap = new Map<string | null, TreeItem[]>()
  
  // First, organize folders by parent
  props.folders.forEach(folder => {
    const treeFolder: TreeItem = {
      id: folder.id,
      type: 'folder',
      name: folder.name,
      data: folder,
      children: [],
      isExpanded: folder.isExpanded
    }
    
    const parentId = folder.parent || null
    if (!folderMap.has(parentId)) {
      folderMap.set(parentId, [])
    }
    folderMap.get(parentId)!.push(treeFolder)
  })
  
  // Organize documents by folder
  const docsByFolder = new Map<string | null, Document[]>()
  props.documents.forEach(doc => {
    const folderId = doc.folder || null
    if (!docsByFolder.has(folderId)) {
      docsByFolder.set(folderId, [])
    }
    docsByFolder.get(folderId)!.push(doc)
  })
  
  // Build tree recursively
  function buildTree(parentId: string | null = null): TreeItem[] {
    const items: TreeItem[] = []
    
    // Add folders for this level
    const folders = folderMap.get(parentId) || []
    folders.forEach(folder => {
      // Add child folders and documents to this folder
      folder.children = [
        ...buildTree(folder.id), // Child folders
        ...(docsByFolder.get(folder.id) || []).map(doc => ({ // Documents in this folder
          id: doc.id,
          type: 'document' as const,
          name: doc.displayName,
          data: doc
        }))
      ]
      items.push(folder)
    })
    
    // Add root documents (only at root level)
    if (parentId === null) {
      const rootDocs = docsByFolder.get(null) || []
      rootDocs.forEach(doc => {
        items.push({
          id: doc.id,
          type: 'document',
          name: doc.displayName,
          data: doc
        })
      })
    }
    
    return items
  }
  
  return buildTree()
})

function handleSelect(item: TreeItem) {
  emit('select', item)
}

function handleToggle(folderId: string) {
  emit('toggle', folderId)
}
</script>