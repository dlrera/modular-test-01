"""
PM Template serializers.
"""
from rest_framework import serializers
from .models import PMTemplate


class PMTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for PMTemplate model.
    """
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = PMTemplate
        fields = [
            'id', 'name', 'description', 'category', 'frequency',
            'tasks', 'task_count', 'ai_generated', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['tenant', 'created_by', 'created_at', 'updated_at']
    
    def get_task_count(self, obj):
        """Get count of tasks in template."""
        return len(obj.tasks) if obj.tasks else 0