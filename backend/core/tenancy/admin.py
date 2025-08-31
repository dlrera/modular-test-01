"""
Admin configuration for tenant models.
"""
from django.contrib import admin
from .models import Account, UserProfile


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'contact_email']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'account', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'account']
    search_fields = ['user__username', 'user__email', 'account__name']
    raw_id_fields = ['user']