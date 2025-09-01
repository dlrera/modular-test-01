<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="600"
    persistent
  >
    <v-card>
      <v-card-title class="text-h5 bg-primary text-white">
        Upload Document
      </v-card-title>
      
      <v-form @submit.prevent="handleSubmit" ref="form">
        <v-card-text class="pt-6">
          <!-- File Upload Area -->
          <div
            class="upload-zone pa-6 text-center rounded-lg mb-4"
            :class="{ 'drag-over': isDragging }"
            @drop.prevent="handleDrop"
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
          >
            <v-icon size="48" class="text-medium-emphasis mb-2">
              mdi-cloud-upload
            </v-icon>
            <p class="text-body-1 mb-2">
              Drag and drop your file here
            </p>
            <p class="text-body-2 text-medium-emphasis mb-4">
              or
            </p>
            <v-btn
              variant="outlined"
              @click="$refs.fileInput.click()"
            >
              Browse Files
            </v-btn>
            <input
              ref="fileInput"
              type="file"
              hidden
              @change="handleFileSelect"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.jpg,.jpeg,.png,.gif"
            />
          </div>

          <!-- Selected File Display -->
          <v-alert
            v-if="formData.file"
            type="info"
            variant="tonal"
            closable
            @click:close="formData.file = null"
            class="mb-4"
          >
            <div class="d-flex align-center">
              <v-icon :icon="getFileIcon(formData.file.type)" class="mr-2" />
              <div>
                <div>{{ formData.file.name }}</div>
                <div class="text-caption">{{ formatFileSize(formData.file.size) }}</div>
              </div>
            </div>
          </v-alert>

          <!-- File Metadata -->
          <v-text-field
            v-model="formData.nickname"
            label="Nickname (Optional)"
            hint="Display name for the file (original name used if empty)"
            variant="outlined"
            class="mb-4"
          />

          <v-textarea
            v-model="formData.description"
            label="Description (Optional)"
            variant="outlined"
            rows="3"
            class="mb-4"
          />

          <!-- Folder Selection -->
          <v-select
            v-model="formData.folder"
            :items="folderOptions"
            label="Folder"
            variant="outlined"
            item-title="name"
            item-value="id"
            class="mb-4"
          >
            <template v-slot:prepend-inner>
              <v-icon>mdi-folder</v-icon>
            </template>
          </v-select>

          <!-- Share Settings -->
          <v-expansion-panels variant="accordion" class="mb-4">
            <v-expansion-panel>
              <v-expansion-panel-title>
                <v-icon class="mr-2">mdi-share-variant</v-icon>
                Share with Users
              </v-expansion-panel-title>
              <v-expansion-panel-text>
                <v-autocomplete
                  v-model="formData.shareWith"
                  :items="users"
                  label="Select users to share with"
                  variant="outlined"
                  multiple
                  chips
                  closable-chips
                  item-title="fullName"
                  item-value="id"
                />
              </v-expansion-panel-text>
            </v-expansion-panel>
          </v-expansion-panels>

          <!-- AI Parser (Future Feature) -->
          <v-alert
            type="info"
            variant="tonal"
            class="mb-4"
          >
            <v-icon class="mr-2">mdi-robot</v-icon>
            AI Document Parser - Coming Soon
          </v-alert>

          <!-- Upload Constraints Warning -->
          <v-alert
            v-if="uploadError"
            type="error"
            variant="tonal"
            closable
            @click:close="uploadError = ''"
          >
            {{ uploadError }}
          </v-alert>
        </v-card-text>

        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="handleCancel"
            :disabled="uploading"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            type="submit"
            :loading="uploading"
            :disabled="!formData.file"
          >
            Upload
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useDocumentsStore } from '../stores/documentsStore'
import type { UploadFormData, User } from '../types'

const props = defineProps<{
  modelValue: boolean
  currentFolder: string | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'upload': [formData: UploadFormData]
}>()

const store = useDocumentsStore()

// Reactive state
const form = ref()
const fileInput = ref()
const isDragging = ref(false)
const uploading = ref(false)
const uploadError = ref('')
const users = ref<User[]>([])

const formData = reactive<UploadFormData>({
  file: null,
  folder: props.currentFolder,
  nickname: '',
  description: '',
  shareWith: []
})

// Computed
const folderOptions = computed(() => {
  const options = [{ id: null, name: 'Root' }]
  // Flatten folder tree for select options
  const flatten = (folders: any[], level = 0) => {
    folders.forEach(folder => {
      options.push({
        id: folder.id,
        name: '  '.repeat(level) + folder.name
      })
      if (folder.children) {
        flatten(folder.children, level + 1)
      }
    })
  }
  flatten(store.folderTree)
  return options
})

// Watch for current folder changes
watch(() => props.currentFolder, (value) => {
  formData.folder = value
})

// Initialize
onMounted(async () => {
  // Load users for sharing
  // users.value = await loadUsers()
})

// Handlers
function handleDrop(event: DragEvent) {
  isDragging.value = false
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    handleFile(files[0])
  }
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    handleFile(target.files[0])
  }
}

function handleFile(file: File) {
  // Validate file
  const maxSize = 100 * 1024 * 1024 // 100MB
  if (file.size > maxSize) {
    uploadError.value = `File size exceeds maximum allowed size of ${formatFileSize(maxSize)}`
    return
  }

  const blockedExtensions = ['.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar', '.msi', '.app']
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (blockedExtensions.includes(ext)) {
    uploadError.value = `File type ${ext} is not allowed`
    return
  }

  formData.file = file
  uploadError.value = ''
}

async function handleSubmit() {
  if (!form.value.validate()) return
  if (!formData.file) return

  uploading.value = true
  uploadError.value = ''

  try {
    await emit('upload', { ...formData })
    handleCancel()
  } catch (error: any) {
    uploadError.value = error.response?.data?.error || 'Upload failed'
  } finally {
    uploading.value = false
  }
}

function handleCancel() {
  emit('update:modelValue', false)
  // Reset form
  formData.file = null
  formData.nickname = ''
  formData.description = ''
  formData.shareWith = []
  uploadError.value = ''
}

// Utilities
function getFileIcon(mimeType: string): string {
  if (mimeType.includes('word')) return 'mdi-file-word'
  if (mimeType.includes('excel') || mimeType.includes('spreadsheet')) return 'mdi-file-excel'
  if (mimeType.includes('pdf')) return 'mdi-file-pdf-box'
  if (mimeType.includes('image')) return 'mdi-file-image'
  if (mimeType.includes('csv')) return 'mdi-file-delimited'
  if (mimeType.includes('text')) return 'mdi-file-document'
  return 'mdi-file'
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
</script>

<style scoped>
.upload-zone {
  border: 2px dashed rgba(0, 0, 0, 0.2);
  transition: all 0.3s;
}

.upload-zone.drag-over {
  border-color: var(--v-primary-base);
  background-color: rgba(33, 96, 147, 0.05);
}
</style>