# Project Guidelines for Claude

## Project Overview
Multi-tenant Property Management (PM) application with strict tenant isolation, built as a mono-repo with Django REST Framework backend and Vue.js frontend.

## Architecture Principles

### 1. **API-First Development**
- Define OpenAPI contracts in `backend/api/contracts/v1/` before implementation
- Use drf-spectacular for auto-documentation at `/api/v1/schema`
- Generate TypeScript types from OpenAPI for frontend

### 2. **Strict Tenant Isolation**
- Every database query MUST filter by `tenant_id`
- Use `TenantAwareModel` base class for all models
- Request middleware sets active tenant from user's account
- S3 keys include tenant ID: `tenants/{tenant_id}/documents/{doc_id}`

### 3. **Test Coverage Requirements**
- Maintain 85-90% test coverage to merge
- Every API endpoint needs contract tests
- Every model needs a factory (using factory_boy)
- Frontend components need Vitest unit tests

## Commands to Run

### Before Committing Code
```bash
# Backend Testing & Linting
cd backend
pytest --cov --cov-report=term-missing
black --check .
isort --check-only .
mypy .
ruff check .
djlint templates/

# Frontend Testing & Linting  
cd frontend
npm run test
npm run type-check
npm run lint
npm run format -- --check
```

### Development Commands
```bash
# Start all services
docker-compose up -d

# Backend development
cd backend
python manage.py runserver
celery -A config worker -l info

# Frontend development
cd frontend
npm run dev

# Database migrations
cd backend
python manage.py makemigrations
python manage.py migrate
```

## Project Structure

### Backend File Organization
```
backend/
├── config/              # Django settings
│   ├── settings/
│   │   ├── base.py     # Shared settings
│   │   └── dev.py      # Development settings
│   ├── celery.py       # Celery configuration
│   └── urls.py         # Root URL config
├── core/               # Shared core functionality
│   ├── auth/           # Authentication & authorization
│   ├── tenancy/        # Tenant isolation utilities
│   ├── storage/        # S3 storage abstractions
│   └── utils/          # Shared utilities
├── modules/            # Feature modules
│   ├── documents/
│   ├── pm_templates/
│   └── risk_inspections/
└── api/
    └── contracts/v1/   # OpenAPI specifications
```

### Frontend File Organization
```
frontend/
├── src/
│   ├── features/       # Feature modules (match backend)
│   │   ├── documents/
│   │   ├── pm-templates/
│   │   └── risk-inspections/
│   ├── shared/         # Shared code
│   │   ├── components/ # Reusable components
│   │   ├── services/   # API clients
│   │   └── utils/      # Helper functions
│   └── router/         # Vue Router config
```

## Module Development Pattern

### Creating a New Backend Module
1. Create directory: `backend/modules/{module_name}/`
2. Create standard files:
   ```python
   # models.py
   from core.tenancy.models import TenantAwareModel
   
   class MyModel(TenantAwareModel):
       # Your fields here
       pass
   
   # serializers.py
   from rest_framework import serializers
   from .models import MyModel
   
   class MyModelSerializer(serializers.ModelSerializer):
       class Meta:
           model = MyModel
           fields = '__all__'
           read_only_fields = ['tenant_id']
   
   # views.py
   from rest_framework import viewsets
   from core.tenancy.views import TenantAwareViewSet
   from .models import MyModel
   from .serializers import MyModelSerializer
   
   class MyModelViewSet(TenantAwareViewSet):
       queryset = MyModel.objects.all()
       serializer_class = MyModelSerializer
   
   # urls.py
   from rest_framework.routers import DefaultRouter
   from .views import MyModelViewSet
   
   router = DefaultRouter()
   router.register('items', MyModelViewSet)
   urlpatterns = router.urls
   ```
3. Add to `INSTALLED_APPS` in settings
4. Create migrations: `python manage.py makemigrations {module_name}`
5. Create tests in `tests/test_{module_name}.py`

### Creating a New Frontend Feature
1. Create directory: `frontend/src/features/{feature-name}/`
2. Create standard structure:
   ```
   features/{feature-name}/
   ├── components/       # Vue components
   ├── composables/      # Vue composables
   ├── services/         # API service
   ├── stores/          # Pinia stores
   ├── types/           # TypeScript types
   └── index.ts         # Public exports
   ```

## Tenant Isolation Rules

### DO ✅
- Always use `TenantAwareModel` as base class
- Filter all queries through `TenantAwareQuerySet`
- Include tenant context in Celery tasks
- Scope S3 paths by tenant ID
- Validate tenant access in serializers

### DON'T ❌
- Never query across tenants (even for admins)
- Don't bypass tenant filters for "superuser" access
- Never expose tenant_id in API responses
- Don't share cache keys between tenants

## Authentication & Authorization

### User Roles
- **admin**: Full access within their tenant
- **manager**: Can manage most resources
- **user**: Limited read/write access

### Permission Pattern
```python
from core.auth.permissions import RoleBasedPermission

class DocumentViewSet(TenantAwareViewSet):
    permission_classes = [RoleBasedPermission]
    role_permissions = {
        'list': ['user', 'manager', 'admin'],
        'create': ['manager', 'admin'],
        'destroy': ['admin']
    }
```

## API Versioning Strategy

### URL Structure
- Current version: `/api/v1/`
- Deprecated versions supported for 6 months
- Version bump for breaking changes only

### Contract Changes
- **Non-breaking**: Add optional fields, new endpoints
- **Breaking**: Remove fields, change types, rename fields
- Document all changes in `docs/API_CHANGELOG.md`

## Background Jobs (Celery)

### Task Categories
- **email**: Email sending tasks
- **documents**: Thumbnail generation, OCR processing
- **reports**: Report generation, export tasks
- **maintenance**: Cleanup, archival tasks

### Task Pattern
```python
from celery import shared_task
from core.tenancy.tasks import tenant_aware_task

@shared_task
@tenant_aware_task
def process_document(tenant_id, document_id):
    # Task implementation
    pass
```

## Testing Guidelines

### Backend Testing
```python
# Use factories for test data
from factory import Factory
from modules.documents.models import Document

class DocumentFactory(Factory):
    class Meta:
        model = Document
    
    title = factory.Faker('sentence')
    tenant_id = factory.SubFactory(TenantFactory)

# Test pattern
def test_document_list_filters_by_tenant(api_client, tenant):
    # Setup
    doc1 = DocumentFactory(tenant=tenant)
    doc2 = DocumentFactory()  # Different tenant
    
    # Act
    response = api_client.get('/api/v1/documents/')
    
    # Assert
    assert len(response.data) == 1
    assert response.data[0]['id'] == doc1.id
```

### Frontend Testing
```typescript
// Component test pattern
import { mount } from '@vue/test-utils'
import DocumentList from './DocumentList.vue'

describe('DocumentList', () => {
  it('filters documents by search term', async () => {
    const wrapper = mount(DocumentList, {
      props: { documents: mockDocuments }
    })
    
    await wrapper.find('input').setValue('test')
    
    expect(wrapper.findAll('.document-item')).toHaveLength(1)
  })
})
```

## Security Checklist

⚠️ **CRITICAL Security Rules**
1. **NEVER** commit secrets, API keys, or passwords
2. **ALWAYS** use environment variables for sensitive data
3. **VALIDATE** all user input on backend (never trust frontend)
4. **SANITIZE** file uploads (check type, size, scan for malware)
5. **RATE LIMIT** all API endpoints
6. **LOG** all authentication attempts and permission denials
7. **ENCRYPT** sensitive data at rest (PII, financial data)
8. **USE HTTPS** everywhere (enforce in production)

## Performance Guidelines

### Database
- Index foreign keys and filter fields
- Use `select_related()` and `prefetch_related()`
- Paginate all list endpoints (default 50, max 200)

### Caching
- Cache expensive queries with Redis
- Use tenant-scoped cache keys
- Default TTL: 5 minutes for lists, 1 hour for detail views

### Frontend
- Lazy load route components
- Use virtual scrolling for long lists
- Implement proper loading states
- Debounce search inputs (300ms)

## Code Style Preferences

### Python
- Type hints for all functions
- Docstrings for classes and public methods
- Max line length: 88 (Black default)
- Import order: stdlib, third-party, local

### TypeScript/Vue
- Composition API with `<script setup>`
- Type all props and emits
- Use `interface` over `type` for objects
- Prefer `const` assertions

## Deployment Notes

### Environment Variables Required
```bash
# Django
SECRET_KEY=
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
CELERY_BROKER_URL=redis://...

# S3/MinIO
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_ENDPOINT_URL=  # For MinIO

# Email
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

# Monitoring (optional)
SENTRY_DSN=
```

## Common Issues & Solutions

### Issue: Tenant isolation breach
**Solution**: Check that view inherits from `TenantAwareViewSet` and model from `TenantAwareModel`

### Issue: Migration conflicts
**Solution**: Run `python manage.py makemigrations --merge`

### Issue: TypeScript types out of sync
**Solution**: Regenerate from OpenAPI: `npm run generate-types`

### Issue: Celery tasks not processing
**Solution**: Check Redis is running and worker is started with correct queue

## Questions?
For architectural decisions, see `docs/ADR/`
For specific module details, see module README files
For deployment, see `docs/DEPLOYMENT.md`