"""
Risk inspection API views.
"""
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from core.tenancy.views import TenantAwareViewSet
from core.auth.permissions import RoleBasedPermission
from .models import RiskInspection, InspectionFinding
from .serializers import RiskInspectionSerializer, InspectionFindingSerializer
from .services import RiskInspectionService


class RiskInspectionViewSet(TenantAwareViewSet):
    """
    API viewset for risk inspection management.
    """
    queryset = RiskInspection.objects.all()
    serializer_class = RiskInspectionSerializer
    permission_classes = [RoleBasedPermission]
    
    role_permissions = {
        'list': ['user', 'manager', 'admin'],
        'retrieve': ['user', 'manager', 'admin'],
        'create': ['manager', 'admin'],
        'update': ['manager', 'admin'],
        'partial_update': ['manager', 'admin'],
        'destroy': ['admin'],
        'add_finding': ['manager', 'admin'],
        'export_report': ['user', 'manager', 'admin'],
    }
    
    def get_queryset(self):
        """Override to prefetch findings."""
        queryset = super().get_queryset()
        return queryset.prefetch_related('findings')
    
    @action(detail=True, methods=['post'])
    def add_finding(self, request, pk=None):
        """
        Add a finding to an inspection.
        """
        inspection = self.get_object()
        serializer = InspectionFindingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create finding
        finding = InspectionFinding.objects.create(
            tenant=request.tenant,
            created_by=request.user,
            inspection=inspection,
            **serializer.validated_data
        )
        
        # Update overall risk
        service = RiskInspectionService(request.user, request.tenant)
        service._update_overall_risk(inspection)
        
        return Response(
            InspectionFindingSerializer(finding).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def export_report(self, request, pk=None):
        """
        Export inspection report.
        TODO: Implement PDF/Excel export.
        """
        inspection = self.get_object()
        service = RiskInspectionService(request.user, request.tenant)
        report = service.generate_report(inspection.id)
        
        if report:
            # For now, return report data as JSON
            # TODO: Generate actual PDF/Excel file
            return Response({
                'site_name': report.site_name,
                'inspection_date': report.inspection_date,
                'overall_risk_level': report.overall_risk_level,
                'findings_count': report.findings_count,
                'high_risk_count': report.high_risk_count,
                'estimated_total_cost': report.estimated_total_cost,
                'export_format': 'json',  # TODO: Support pdf, excel
            })
        
        return Response(
            {'error': 'Report generation failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )