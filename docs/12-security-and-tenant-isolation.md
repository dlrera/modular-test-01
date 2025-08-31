# Security and tenant isolation

### Data model
- `Account` is the tenant.
- All module models inherit from `TenantBaseModel` which includes `tenant` FK and `created_by`.

### Query safety
- Custom manager `TenantManager` applies `tenant` filter automatically when a request context is active.
- Views resolve the current tenant from the authenticated user’s selected account.

### Permissions
- Check role (admin, manager, user) at service boundary. Admin can manage users in the same tenant.

### Files
- S3 prefixes include tenant id. Access is checked server-side; clients never see raw S3 keys.

### Example base model
```python
# core/tenancy/models.py
from django.db import models
from django.contrib.auth import get_user_model

class TenantBaseModel(models.Model):
    tenant = models.ForeignKey('core_tenancy.Account', on_delete=models.CASCADE)
    created_by = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

### Example manager and middleware
- Add a request-local storage (thread-local or contextvar) for `current_tenant`.
- Manager reads it to auto-filter.