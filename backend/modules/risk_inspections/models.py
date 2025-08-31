"""
Risk inspection models.
"""
from django.db import models
from core.tenancy.models import TenantBaseModel


class RiskInspection(TenantBaseModel):
    """
    Risk inspection for a site/location.
    """
    site_name = models.CharField(max_length=255)
    inspection_date = models.DateField()
    inspector_name = models.CharField(max_length=255)
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Overall risk assessment
    overall_risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        blank=True
    )
    
    # Summary and recommendations
    summary = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    class Meta:
        db_table = 'risk_inspections'
        ordering = ['-inspection_date', '-created_at']
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['tenant', 'inspection_date']),
        ]
    
    def __str__(self):
        return f"{self.site_name} - {self.inspection_date}"


class InspectionFinding(TenantBaseModel):
    """
    Individual finding within a risk inspection.
    """
    inspection = models.ForeignKey(
        RiskInspection,
        on_delete=models.CASCADE,
        related_name='findings'
    )
    
    category = models.CharField(max_length=100)
    description = models.TextField()
    
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ]
    )
    
    # Mitigation strategy
    mitigation_strategy = models.TextField(blank=True)
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    
    # Photos stored as JSON array of S3 keys
    photos = models.JSONField(default=list, blank=True)
    
    # Resolution tracking
    is_resolved = models.BooleanField(default=False)
    resolution_date = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'inspection_findings'
        ordering = ['-risk_level', 'category']
    
    def __str__(self):
        return f"{self.category}: {self.risk_level}"