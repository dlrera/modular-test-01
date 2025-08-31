# Config and secrets

- All secrets and keys come from environment variables.
- `settings_dev.py` reads from `.env` for local only. `.env` never committed.
- Future: use AWS SSM or Secrets Manager.
- Required variables documented in `README.md`.