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

### Test pattern
- Unit tests focus on `services/`.
- API tests verify request/response and tenant scoping.