# Service layer standard

- Services take a `user` and `tenant` when needed.
- Inputs and outputs are DTOs (dataclasses or TypedDict) with explicit types.
- No ORM access in views; only in services/repositories.
- Errors raise domain exceptions; views map to HTTP codes.
- Idempotency for tasks that may retry.
- Logging includes request id and tenant id.