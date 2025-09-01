<template>
  <v-list density="compact" class="pa-0">
    <!-- Root folder -->
    <v-list-item
      @click="$emit('select', null)"
      :active="currentFolder === null"
      prepend-icon="mdi-folder-home"
    >
      <v-list-item-title>Root</v-list-item-title>
    </v-list-item>
    
    <!-- Folder tree -->
    <template v-for="folder in folders" :key="folder.id">
      <FolderTreeItem
        :folder="folder"
        :current-folder="currentFolder"
        :level="0"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </template>
  </v-list>
</template>

<script setup lang="ts">
import type { Folder } from '../types'
import FolderTreeItem from './FolderTreeItem.vue'

defineProps<{
  folders: Folder[]
  currentFolder: string | null
}>()

defineEmits<{
  select: [folderId: string | null]
  toggle: [folderId: string]
}>()
</script>