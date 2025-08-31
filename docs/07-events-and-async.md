# Events and async jobs

- Use Celery with Redis for background jobs.
- Common tasks: send emails, generate thumbnails, index documents, render inspection reports.
- Task rules: small inputs, idempotent, retries with backoff, log request id + tenant id.
- Optional: simple domain events later. Start with tasks only.
- Email provider TBD; in dev, use Django's console email backend.