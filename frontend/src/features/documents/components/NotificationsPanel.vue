<template>
  <v-navigation-drawer
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    location="right"
    temporary
    width="400"
  >
    <v-list-item class="pa-4">
      <v-list-item-title class="text-h6">
        Notifications
      </v-list-item-title>
      <template v-slot:append>
        <v-btn
          icon
          size="small"
          @click="$emit('update:modelValue', false)"
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </template>
    </v-list-item>
    
    <v-divider />
    
    <v-list v-if="notifications.length > 0" class="pa-0">
      <v-list-item
        v-for="notification in notifications"
        :key="notification.id"
        class="pa-4"
        :class="{ 'bg-grey-lighten-5': !notification.isRead }"
      >
        <template v-slot:prepend>
          <v-icon :color="getNotificationColor(notification.notificationType)">
            {{ getNotificationIcon(notification.notificationType) }}
          </v-icon>
        </template>
        
        <v-list-item-title class="mb-1">
          {{ getNotificationTitle(notification) }}
        </v-list-item-title>
        
        <v-list-item-subtitle>
          <div>{{ notification.documentName }}</div>
          <div class="text-caption">
            {{ formatRelativeTime(notification.createdAt) }}
          </div>
        </v-list-item-subtitle>
        
        <template v-slot:append v-if="notification.notificationType === 'share_received' && notification.shareStatus === 'pending'">
          <div class="d-flex ga-2">
            <v-btn
              size="small"
              color="success"
              variant="tonal"
              @click="handleAccept(notification)"
            >
              Accept
            </v-btn>
            <v-btn
              size="small"
              color="error"
              variant="tonal"
              @click="handleReject(notification)"
            >
              Reject
            </v-btn>
          </div>
        </template>
      </v-list-item>
    </v-list>
    
    <div v-else class="text-center pa-8">
      <v-icon size="48" class="text-medium-emphasis mb-4">
        mdi-bell-outline
      </v-icon>
      <p class="text-body-1 text-medium-emphasis">
        No new notifications
      </p>
    </div>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import type { ShareNotification } from '../types'

defineProps<{
  modelValue: boolean
  notifications: ShareNotification[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'accept': [shareId: string]
  'reject': [shareId: string]
  'mark-read': [notificationId: string]
}>()

function getNotificationIcon(type: string): string {
  const icons: Record<string, string> = {
    share_received: 'mdi-share-variant',
    share_accepted: 'mdi-check-circle',
    share_rejected: 'mdi-close-circle',
    share_revoked: 'mdi-cancel'
  }
  return icons[type] || 'mdi-bell'
}

function getNotificationColor(type: string): string {
  const colors: Record<string, string> = {
    share_received: 'info',
    share_accepted: 'success',
    share_rejected: 'warning',
    share_revoked: 'error'
  }
  return colors[type] || 'primary'
}

function getNotificationTitle(notification: ShareNotification): string {
  switch (notification.notificationType) {
    case 'share_received':
      return `${notification.sharedByName} shared a document with you`
    case 'share_accepted':
      return `Share accepted`
    case 'share_rejected':
      return `Share rejected`
    case 'share_revoked':
      return `Share revoked by ${notification.sharedByName}`
    default:
      return 'New notification'
  }
}

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`
  return `${days} day${days > 1 ? 's' : ''} ago`
}

function handleAccept(notification: ShareNotification) {
  emit('accept', notification.documentShare)
  emit('mark-read', notification.id)
}

function handleReject(notification: ShareNotification) {
  emit('reject', notification.documentShare)
  emit('mark-read', notification.id)
}
</script>