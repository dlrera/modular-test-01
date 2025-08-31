"""
Core tenant isolation models and managers.

This module provides the foundation for multi-tenant data isolation
throughout the application.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from contextvars import ContextVar

# Thread-safe context variable for current tenant
current_tenant = ContextVar('current_tenant', default=None)


class Account(models.Model):
    """
    Represents a tenant/account in the system.
    All data is scoped to an Account for strict tenant isolation.
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional fields for account details
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    class Meta:
        db_table = 'accounts'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class TenantManager(models.Manager):
    """
    Custom manager that automatically filters queries by current tenant.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        tenant = current_tenant.get()
        if tenant:
            # Auto-filter by tenant if context is set
            return queryset.filter(tenant=tenant)
        return queryset
    
    def all_tenants(self):
        """Get unfiltered queryset for admin operations."""
        return super().get_queryset()


class TenantBaseModel(models.Model):
    """
    Abstract base model that includes tenant scoping.
    All tenant-aware models should inherit from this.
    """
    tenant = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='%(app_label)s_%(class)s_set'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='%(app_label)s_%(class)s_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = TenantManager()
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['tenant', 'created_at']),
        ]


class UserProfile(models.Model):
    """
    Extended user profile linking users to accounts and roles.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    ]
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name='users'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_profiles'
        unique_together = ['user', 'account']
    
    def __str__(self):
        return f"{self.user.username} - {self.account.name} ({self.role})"