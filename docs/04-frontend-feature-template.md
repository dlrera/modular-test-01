# Frontend feature template

> Copy to `frontend/src/features/<feature>`

- `routes.ts`: routes under `/app/<feature>`
- `store.ts`: Pinia store for this feature
- `components/`: UI components
- `services/`: calls typed API client
- `tests/`: component and store tests

### API client
Use generated client from `src/shared/api/<module>/client.ts`.

### Example store
```ts
import { defineStore } from 'pinia'
import { DocumentsApi } from '@/shared/api/documents/client'

export const useDocumentsStore = defineStore('documents', {
  state: () => ({ items: [], loading: false }),
  actions: {
    async fetchList() {
      this.loading = true
      try { this.items = await new DocumentsApi().listDocuments() } finally { this.loading = false }
    }
  }
})
```