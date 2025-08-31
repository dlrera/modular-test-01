"""
Risk Inspections app configuration.
"""
from django.apps import AppConfig


class RiskInspectionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.risk_inspections'
    verbose_name = 'Risk Inspections'