<template>
  <div>
    <v-list-item
      @click="handleClick"
      :active="currentFolder === folder.id"
      :style="{ paddingLeft: `${16 + level * 16}px` }"
    >
      <template v-slot:prepend>
        <v-icon
          v-if="folder.children && folder.children.length > 0"
          @click.stop="$emit('toggle', folder.id)"
          size="small"
          class="mr-1"
        >
          {{ folder.isExpanded ? 'mdi-chevron-down' : 'mdi-chevron-right' }}
        </v-icon>
        <v-icon size="small">
          {{ folder.isExpanded ? 'mdi-folder-open' : 'mdi-folder' }}
        </v-icon>
      </template>
      
      <v-list-item-title>
        {{ folder.name }}
        <span v-if="folder.documentCount > 0" class="text-caption text-medium-emphasis ml-1">
          ({{ folder.documentCount }})
        </span>
      </v-list-item-title>
    </v-list-item>
    
    <!-- Child folders -->
    <template v-if="folder.isExpanded && folder.children">
      <FolderTreeItem
        v-for="child in folder.children"
        :key="child.id"
        :folder="child"
        :current-folder="currentFolder"
        :level="level + 1"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import type { Folder } from '../types'

const props = defineProps<{
  folder: Folder
  currentFolder: string | null
  level: number
}>()

const emit = defineEmits<{
  select: [folderId: string]
  toggle: [folderId: string]
}>()

function handleClick() {
  emit('select', props.folder.id)
}
</script>