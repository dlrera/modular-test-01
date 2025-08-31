# Architecture principles

1. **Single repo, modular code**
   - Backend modules live in `backend/modules/<name>`.
   - Frontend features live in `frontend/src/features/<name>`.

2. **Clear boundaries**
   - No direct imports across modules except through `public/` interfaces.
   - Cross-module calls happen via service interfaces or background tasks.

3. **Service layer**
   - Views and API endpoints call services. Services encapsulate domain logic and data access.

4. **Tenant safety**
   - Base model adds `tenant_id`. QuerySets auto-apply tenant filters. Permission checks validate tenant access.

5. **API-first and versioned**
   - Write or update OpenAPI before implementing. Generate clients for the frontend.

6. **Storage rules**
   - S3 keys include `tenant_id/module/...`. Never store cross-tenant files in the same path.

7. **Testing is non-negotiable**
   - Unit tests for services and repositories. Contract tests for public interfaces. API schema snapshots.

8. **Minimal shared code**
   - Shared utilities live in `core/*`. Keep them small to avoid coupling.

9. **Change management**
   - Small PRs. Coverage gate. Required reviews can be enabled per path.