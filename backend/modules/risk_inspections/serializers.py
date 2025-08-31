"""
Risk inspection serializers.
"""
from rest_framework import serializers
from .models import RiskInspection, InspectionFinding


class InspectionFindingSerializer(serializers.ModelSerializer):
    """
    Serializer for inspection findings.
    """
    class Meta:
        model = InspectionFinding
        fields = [
            'id', 'category', 'description', 'risk_level',
            'mitigation_strategy', 'estimated_cost', 'photos',
            'is_resolved', 'resolution_date', 'resolution_notes',
            'created_at'
        ]
        read_only_fields = ['tenant', 'created_by', 'created_at']


class RiskInspectionSerializer(serializers.ModelSerializer):
    """
    Serializer for risk inspections.
    """
    findings = InspectionFindingSerializer(many=True, read_only=True)
    findings_count = serializers.SerializerMethodField()
    high_risk_count = serializers.SerializerMethodField()
    
    class Meta:
        model = RiskInspection
        fields = [
            'id', 'site_name', 'inspection_date', 'inspector_name',
            'status', 'overall_risk_level', 'summary', 'recommendations',
            'findings', 'findings_count', 'high_risk_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['tenant', 'created_by', 'created_at', 'updated_at']
    
    def get_findings_count(self, obj):
        """Get total number of findings."""
        return obj.findings.count()
    
    def get_high_risk_count(self, obj):
        """Get count of high/critical risk findings."""
        return obj.findings.filter(risk_level__in=['high', 'critical']).count()