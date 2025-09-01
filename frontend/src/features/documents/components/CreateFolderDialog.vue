<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    max-width="400"
  >
    <v-card>
      <v-card-title class="text-h5 bg-primary text-white">
        Create Folder
      </v-card-title>
      
      <v-form @submit.prevent="handleSubmit" ref="form">
        <v-card-text class="pt-6">
          <v-text-field
            v-model="folderName"
            label="Folder Name"
            variant="outlined"
            :rules="[rules.required]"
            autofocus
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
            Create
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  modelValue: boolean
  parentFolder: string | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'create': [name: string]
}>()

const form = ref()
const folderName = ref('')

const rules = {
  required: (v: any) => !!v || 'Folder name is required'
}

async function handleSubmit() {
  const valid = await form.value.validate()
  if (!valid.valid) return
  
  emit('create', folderName.value)
  handleCancel()
}

function handleCancel() {
  folderName.value = ''
  emit('update:modelValue', false)
}
</script>