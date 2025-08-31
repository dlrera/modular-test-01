# API contracts

- Contracts live in `api/contracts/v1/*.yaml`.
- Update contracts before writing code.
- Generate clients:
  - Backend: drf-spectacular publishes `/api/v1/schema`.
  - Frontend: `openapi-typescript` to `frontend/src/shared/api/<module>/client.ts`.
- Versioning: breaking changes require `v2`.
- Snapshot tests ensure contracts do not change unintentionally.