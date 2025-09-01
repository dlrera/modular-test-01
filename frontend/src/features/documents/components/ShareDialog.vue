<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="500"
  >
    <v-card>
      <v-card-title class="text-h5 bg-primary text-white">
        Share Document
      </v-card-title>
      
      <v-form @submit.prevent="handleSubmit" ref="form">
        <v-card-text class="pt-6">
          <div v-if="document" class="mb-4">
            <p class="text-body-2 text-medium-emphasis">Sharing:</p>
            <p class="text-body-1 font-weight-medium">{{ document.displayName }}</p>
          </div>
          
          <v-autocomplete
            v-model="selectedUsers"
            :items="users"
            label="Select users to share with"
            variant="outlined"
            multiple
            chips
            closable-chips
            item-title="fullName"
            item-value="id"
            :rules="[rules.required]"
            class="mb-4"
          />
          
          <v-textarea
            v-model="message"
            label="Message (Optional)"
            variant="outlined"
            rows="3"
            class="mb-4"
          />
          
          <p class="text-body-2 font-weight-medium mb-2">Permissions:</p>
          
          <v-checkbox
            v-model="permissions.canDownload"
            label="Can download"
            color="primary"
            class="mb-2"
          />
          
          <v-checkbox
            v-model="permissions.canShare"
            label="Can share with others"
            color="primary"
            class="mb-2"
          />
          
          <v-checkbox
            v-model="permissions.canEdit"
            label="Can edit metadata"
            color="primary"
          />
        </v-card-text>
        
        <v-card-actions>
          <v-spacer />
          <v-btn
            variant="text"
            @click="handleCancel"
          >
            Cancel
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            type="submit"
          >
            Share
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { Document } from '../types'

defineProps<{
  modelValue: boolean
  document: Document | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'share': [userIds: string[], permissions: any]
}>()

const form = ref()
const selectedUsers = ref<string[]>([])
const message = ref('')
const users = ref([]) // Would be loaded from API

const permissions = reactive({
  canDownload: true,
  canShare: false,
  canEdit: false
})

const rules = {
  required: (v: any) => (v && v.length > 0) || 'Select at least one user'
}

async function handleSubmit() {
  const valid = await form.value.validate()
  if (!valid.valid) return
  
  emit('share', selectedUsers.value, {
    ...permissions,
    message: message.value
  })
  handleCancel()
}

function handleCancel() {
  selectedUsers.value = []
  message.value = ''
  permissions.canDownload = true
  permissions.canShare = false
  permissions.canEdit = false
  emit('update:modelValue', false)
}
</script>