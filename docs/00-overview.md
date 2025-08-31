# Overview

## Purpose
A single-repo modular web application for insurance partners. The goal is to build features in isolation so work on one area does not break others.

## Stack
- Backend: Django, DRF, Postgres (AWS RDS), Celery, Redis
- Frontend: Vue 3, TypeScript, Vuetify, Pinia, Vue Router
- Storage: AWS S3 (per-tenant prefixes)
- Dev only environment at start; CI with tests and coverage

## Multi-tenancy
Strict tenant isolation.
- Tenant = **Account**.
- Users belong to exactly **one Account**.
- Every record is scoped to the current account (tenant). Requests must include an active account; queries auto-filter by tenant.
- S3 prefixes and keys include the account id.

## Roles
Roles at start: admin, manager, user. Ability to add roles later.

## API policy
API-first with versioning. v1 under `/api/v1/*`. Breaking changes require a version bump.

## Initial modules
1. **documents**: file upload, tags/metadata, search, preview.
2. **pm_templates**: create and manage preventative maintenance templates. AI-assisted template generation from natural language prompts using system data structures.
3. **risk_inspections**: structured site inspections with findings, photos, mitigation strategies, and report exports.

## Background work
Simple job queue for email, indexing, thumbnailing, report rendering.

## Observability (minimal)
Structured logging with request ids and health endpoints. Optional Sentry or tracing added later.