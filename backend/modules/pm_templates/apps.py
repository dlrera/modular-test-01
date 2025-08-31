"""
PM Templates app configuration.
"""
from django.apps import AppConfig


class PmTemplatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modules.pm_templates'
    verbose_name = 'PM Templates'