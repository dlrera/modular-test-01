# API Integration Guide

## Critical Lessons Learned from Document Management Module Implementation

This guide documents essential patterns and common pitfalls when connecting frontend Vue.js components to Django REST Framework backends.

## 1. Authentication & Permissions During Development

### Problem
- Django REST Framework viewsets that filter by `request.user` will fail with `AnonymousUser` errors when authentication is disabled for testing
- Common error: `TypeError: Cannot cast AnonymousUser to int`

### Solution
During development, temporarily handle anonymous users in:
- ViewSet `get_queryset()` methods
- Serializer methods that access `request.user`
- Permission classes

```python
# views.py - Development pattern
def get_queryset(self):
    queryset = super().get_queryset()
    
    # For development without authentication
    # TODO: Re-enable user filtering when authentication is configured
    from django.contrib.auth.models import AnonymousUser
    if isinstance(self.request.user, AnonymousUser):
        return queryset  # Return all records for testing
    
    # Production code
    return queryset.filter(created_by=self.request.user)
```

```python
# serializers.py - Handle anonymous users
def get_can_share(self, obj):
    request = self.context.get('request')
    if not request:
        return False
    
    # Development check
    from django.contrib.auth.models import AnonymousUser
    if isinstance(request.user, AnonymousUser):
        return True  # Allow all operations for testing
    
    # Production logic here
```

## 2. API Response Format Consistency

### Problem
Django REST Framework returns paginated responses by default, but frontend stores often expect arrays.

### Frontend Pattern
Always handle both paginated and array responses:

```typescript
// stores/moduleStore.ts
async function fetchData() {
  try {
    const response = await api.getData()
    
    // Handle paginated response
    if (response.data.results) {
      data.value = response.data.results
    } else if (Array.isArray(response.data)) {
      data.value = response.data
    } else {
      console.error('Unexpected response format:', response.data)
      data.value = []
    }
  } catch (error) {
    console.error('Failed to fetch data:', error)
    data.value = []
  }
}
```

## 3. URL Configuration Checklist

### Backend URLs Setup
1. **Module URLs** (`backend/modules/<module>/urls.py`):
```python
from rest_framework.routers import DefaultRouter
from .views import ModelViewSet

router = DefaultRouter()
router.register('items', ModelViewSet, basename='item')
urlpatterns = router.urls
```

2. **Main URLs** (`backend/config/urls.py`):
```python
urlpatterns = [
    # API v1 endpoints
    path('api/v1/', include('modules.<module>.urls')),
]
```

3. **Verify endpoints**:
```bash
# Test each endpoint
curl -X GET http://localhost:8000/api/v1/items/
```

### Frontend API Service Pattern
```typescript
// services/moduleApi.ts
const API_BASE = '/api/v1'

export const moduleApi = {
  // Use the exact path from router registration
  listItems: () => api.get(`${API_BASE}/items/`),
  getItem: (id: string) => api.get(`${API_BASE}/items/${id}/`),
  createItem: (data: any) => api.post(`${API_BASE}/items/`, data),
}
```

## 4. Common Integration Issues & Solutions

### Issue 1: Import Errors
**Problem**: `ModuleNotFoundError: No module named 'core.storage.s3'`
**Solution**: Ensure all imports exist before using them. Create mock implementations for testing:

```python
# models.py
def get_s3_url(self, expiration: int = 3600) -> str:
    """Generate pre-signed S3 URL for download"""
    # TODO: Implement proper S3 presigned URL generation
    if self.s3_key:
        return f"http://localhost:9000/{self.s3_bucket}/{self.s3_key}"
    return ""
```

### Issue 2: Tenant Context Missing
**Problem**: `AttributeError: 'WSGIRequest' object has no attribute 'tenant'`
**Solution**: Ensure TenantMiddleware is configured or mock tenant for testing:

```python
# views.py
def get_queryset(self):
    queryset = super().get_queryset()
    # Handle missing tenant context during development
    if hasattr(self.request, 'tenant'):
        queryset = queryset.filter(tenant=self.request.tenant)
    return queryset
```

### Issue 3: CORS Errors
**Problem**: Frontend can't reach backend API
**Solution**: Verify CORS settings in `settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',  # Vite dev server
    'http://127.0.0.1:5173',
]
```

## 5. Testing API Integration

### Manual Testing Checklist
Before considering an API integration complete, verify:

1. **List endpoint works**:
```bash
curl -X GET http://localhost:8000/api/v1/items/ -s | python -m json.tool
```

2. **Create endpoint works**:
```bash
curl -X POST http://localhost:8000/api/v1/items/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Item"}' \
  -s | python -m json.tool
```

3. **Frontend can display data**:
- Check browser console for errors
- Verify network tab shows successful API calls
- Confirm data appears in the UI

### Debugging Commands
```bash
# Check Django is running
curl http://localhost:8000/api/v1/

# Check available endpoints
python manage.py show_urls | grep api

# Test with verbose output
curl -v http://localhost:8000/api/v1/items/

# Monitor Django logs
# Server should show: [Date] "GET /api/v1/items/ HTTP/1.1" 200
```

## 6. Development Workflow

### Recommended Order
1. Create backend models and migrations
2. Create viewsets with minimal permissions for testing
3. Test API endpoints with curl
4. Create frontend API service
5. Create frontend store with error handling
6. Create UI components
7. Test full integration
8. Add authentication and permissions
9. Update tests

### Quick Start Template for New Module

#### Backend (`views.py`):
```python
from rest_framework import viewsets
from core.tenancy.views import TenantAwareViewSet
from .models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(TenantAwareViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    
    # Start with no auth for testing
    permission_classes = []
    authentication_classes = []
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Add filters but handle anonymous users
        return queryset
```

#### Frontend (`stores/myStore.ts`):
```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { myApi } from '../services/myApi'

export const useMyStore = defineStore('myModule', () => {
  const items = ref<any[]>([])
  const loading = ref(false)
  
  async function fetchItems() {
    loading.value = true
    try {
      const response = await myApi.listItems()
      // Handle paginated response
      if (response.data.results) {
        items.value = response.data.results
      } else if (Array.isArray(response.data)) {
        items.value = response.data
      } else {
        items.value = []
      }
    } catch (error) {
      console.error('Failed to fetch items:', error)
      items.value = []
    } finally {
      loading.value = false
    }
  }
  
  return { items, loading, fetchItems }
})
```

## 7. Production Readiness Checklist

Before deploying to production:

- [ ] Re-enable authentication in all viewsets
- [ ] Remove anonymous user bypasses
- [ ] Add proper permission classes
- [ ] Implement proper S3 storage integration
- [ ] Add rate limiting
- [ ] Enable CSRF protection
- [ ] Add comprehensive error handling
- [ ] Test with real authentication flow
- [ ] Verify tenant isolation works correctly
- [ ] Add monitoring and logging

## 8. Common Error Messages Reference

| Error | Cause | Solution |
|-------|-------|----------|
| `TypeError: Cannot cast AnonymousUser to int` | Filtering by request.user without auth | Add AnonymousUser check |
| `ModuleNotFoundError` | Missing import | Create module or mock it |
| `404 Not Found` on API call | URL not registered | Check urls.py inclusion |
| `CORS policy` error | CORS not configured | Update CORS_ALLOWED_ORIGINS |
| `.filter is not a function` | Expected array, got object | Handle paginated response |
| `AttributeError: 'WSGIRequest' object has no attribute 'tenant'` | Middleware not configured | Add TenantMiddleware or mock |

## Summary

The key to successful API integration is:
1. Start with minimal authentication for testing
2. Handle multiple response formats in the frontend
3. Test each endpoint independently before integration
4. Use consistent error handling patterns
5. Document TODO items for production hardening