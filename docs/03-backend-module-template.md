# Backend module template

> Copy this structure into `backend/modules/<your_module>`

### Files
- `models.py`: Django models. Inherit from `core.tenancy.models.TenantBaseModel`.
- `services/`: Pure Python services that implement use-cases.
- `api/`: DRF views/serializers/routers for this module only.
- `tasks/`: Celery tasks for background work.
- `public/`: Public service interfaces (thin wrappers) other modules may call.
- `tests/`: Unit and API tests.
- `urls.py`: Module routes under `/api/v1/<module>/...`.

### Service pattern
```python
# services/example.py
from dataclasses import dataclass

@dataclass
class CreateResult:
    id: int

class ExampleService:
    def __init__(self, user, tenant):
        self.user = user
        self.tenant = tenant

    def create_something(self, dto) -> CreateResult:
        # validate, write models, emit events, return DTO
        ...
```

### Public interface pattern
```python
# public/iface.py
from .services.example import ExampleService

def create_something_public(user, tenant, dto):
    return ExampleService(user, tenant).create_something(dto)
```

### ViewSet pattern for development
```python
# views.py - Start with minimal auth for testing
from rest_framework import viewsets
from core.tenancy.views import TenantAwareViewSet

class MyModelViewSet(TenantAwareViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    
    # Start with no auth for testing
    permission_classes = []
    authentication_classes = []
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Handle anonymous users during development
        from django.contrib.auth.models import AnonymousUser
        if isinstance(self.request.user, AnonymousUser):
            return queryset
        
        # Production: filter by user
        return queryset.filter(created_by=self.request.user)
```

### API Testing before frontend
```bash
# Always test your endpoints first!
curl -X GET http://localhost:8000/api/v1/module/ -s | python -m json.tool
curl -X POST http://localhost:8000/api/v1/module/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test"}' -s | python -m json.tool
```

### Test pattern
- Unit tests focus on `services/`.
- API tests verify request/response and tenant scoping.
- **Manual curl tests before frontend integration**.