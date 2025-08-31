"""
Preventative Maintenance template models.
"""
from django.db import models
from core.tenancy.models import TenantBaseModel


class PMTemplate(TenantBaseModel):
    """
    Preventative Maintenance template.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)
    
    # Template configuration
    frequency = models.CharField(
        max_length=50,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('annually', 'Annually'),
            ('custom', 'Custom'),
        ]
    )
    
    # Task details stored as JSON
    tasks = models.JSONField(default=list)
    
    # AI-generated template metadata
    ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'pm_templates'
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['tenant', 'is_active']),
            models.Index(fields=['tenant', 'category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.frequency})"