# Frontend feature template

> Copy to `frontend/src/features/<feature>`

- `routes.ts`: routes under `/app/<feature>`
- `store.ts`: Pinia store for this feature
- `components/`: UI components
- `services/`: calls typed API client
- `tests/`: component and store tests

### API client
Use generated client from `src/shared/api/<module>/client.ts`.

### Example store with proper response handling
```ts
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { moduleApi } from '../services/moduleApi'

export const useModuleStore = defineStore('module', () => {
  const items = ref<any[]>([])
  const loading = ref(false)
  
  async function fetchItems() {
    loading.value = true
    try {
      const response = await moduleApi.listItems()
      
      // IMPORTANT: Handle paginated responses from Django REST Framework
      if (response.data.results) {
        items.value = response.data.results
      } else if (Array.isArray(response.data)) {
        items.value = response.data
      } else {
        console.error('Unexpected response format:', response.data)
        items.value = []
      }
    } catch (error: any) {
      console.error('Failed to fetch items:', error)
      // Handle 401/403 gracefully during development
      if (error.response?.status === 401 || error.response?.status === 403) {
        items.value = []
      }
    } finally {
      loading.value = false
    }
  }
  
  return { items, loading, fetchItems }
})
```

### API Service Pattern
```ts
// services/moduleApi.ts
import api from '@/services/api'

const API_BASE = '/api/v1'

export const moduleApi = {
  // Match exact paths from Django router registration
  listItems: () => api.get(`${API_BASE}/items/`),
  getItem: (id: string) => api.get(`${API_BASE}/items/${id}/`),
  createItem: (data: any) => api.post(`${API_BASE}/items/`, data),
  updateItem: (id: string, data: any) => api.patch(`${API_BASE}/items/${id}/`, data),
  deleteItem: (id: string) => api.delete(`${API_BASE}/items/${id}/`),
}
```