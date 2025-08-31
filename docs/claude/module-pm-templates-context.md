# Module context: pm_templates

### Purpose
Create and manage preventative maintenance templates. Optional AI-assisted builder that converts natural language into structured templates.

### Public interfaces (backend)
- `pm_templates.public.create_template(user, tenant, dto) -> PMTemplateDTO`
- `pm_templates.public.list_templates(user, tenant, filters) -> list[PMTemplateDTO]`
- `pm_templates.public.generate_from_prompt(user, tenant, prompt, options) -> PMTemplateDTO` (may call external model later)

### API endpoints (v1)
- `POST /api/v1/pm-templates/`
- `GET /api/v1/pm-templates/`
- `POST /api/v1/pm-templates/generate`

### Notes
- DTO includes schedule (frequency, triggers), tasks, parts, and safety steps.
- Keep a stub `AIService` with an interface so the model choice can change later.