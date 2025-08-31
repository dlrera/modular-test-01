# Module context: risk_inspections

### Purpose
Structured inspections for risk. Findings include category, severity, photos, and mitigation suggestions. Export to PDF.

### Public interfaces (backend)
- `risk_inspections.public.create_inspection(user, tenant, dto) -> InspectionDTO`
- `risk_inspections.public.add_finding(user, tenant, inspection_id, dto) -> FindingDTO`
- `risk_inspections.public.export_report(user, tenant, inspection_id) -> str` (returns signed URL)

### Taxonomy
- **Categories**: Life Safety & Egress; Fire Protection & Prevention; Electrical & Mechanical; Building & Structural; Housekeeping & Storage; Environmental & HazMat; Security & Access Control; Special Hazards; Fleet & Grounds
- **Severities**: Critical; High; Moderate; Low/Observation

### API endpoints (v1)
- `POST /api/v1/risk-inspections/`
- `POST /api/v1/risk-inspections/{id}/findings`
- `POST /api/v1/risk-inspections/{id}/export`

### Notes
- Photos stored in S3 under the tenant prefix. Thumbnails generated in background.
- Mitigation suggestions are templated text for now. AI can be added later.