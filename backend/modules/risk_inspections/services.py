"""
Risk inspection service layer.
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import date
from .models import RiskInspection, InspectionFinding


@dataclass
class FindingDTO:
    """DTO for inspection finding."""
    category: str
    description: str
    risk_level: str
    mitigation_strategy: str = ""
    estimated_cost: float = None
    photos: List[str] = None


@dataclass
class InspectionCreateDTO:
    """DTO for creating inspection."""
    site_name: str
    inspection_date: date
    inspector_name: str
    findings: List[FindingDTO] = None


@dataclass
class InspectionReportDTO:
    """DTO for inspection report data."""
    id: int
    site_name: str
    inspection_date: date
    overall_risk_level: str
    findings_count: int
    high_risk_count: int
    estimated_total_cost: float


class RiskInspectionService:
    """
    Service class for risk inspection operations.
    """
    
    def __init__(self, user, tenant):
        self.user = user
        self.tenant = tenant
    
    def create_inspection(self, dto: InspectionCreateDTO) -> InspectionReportDTO:
        """
        Create a new risk inspection with findings.
        """
        # Create inspection
        inspection = RiskInspection.objects.create(
            tenant=self.tenant,
            created_by=self.user,
            site_name=dto.site_name,
            inspection_date=dto.inspection_date,
            inspector_name=dto.inspector_name,
            status='draft'
        )
        
        # Create findings if provided
        if dto.findings:
            for finding_dto in dto.findings:
                InspectionFinding.objects.create(
                    tenant=self.tenant,
                    created_by=self.user,
                    inspection=inspection,
                    category=finding_dto.category,
                    description=finding_dto.description,
                    risk_level=finding_dto.risk_level,
                    mitigation_strategy=finding_dto.mitigation_strategy,
                    estimated_cost=finding_dto.estimated_cost,
                    photos=finding_dto.photos or []
                )
        
        # Calculate overall risk level
        self._update_overall_risk(inspection)
        
        return self._to_report_dto(inspection)
    
    def add_finding(self, inspection_id: int, finding_dto: FindingDTO) -> bool:
        """
        Add a finding to an existing inspection.
        """
        try:
            inspection = RiskInspection.objects.get(
                id=inspection_id,
                tenant=self.tenant
            )
            
            InspectionFinding.objects.create(
                tenant=self.tenant,
                created_by=self.user,
                inspection=inspection,
                category=finding_dto.category,
                description=finding_dto.description,
                risk_level=finding_dto.risk_level,
                mitigation_strategy=finding_dto.mitigation_strategy,
                estimated_cost=finding_dto.estimated_cost,
                photos=finding_dto.photos or []
            )
            
            # Update overall risk
            self._update_overall_risk(inspection)
            
            return True
        except RiskInspection.DoesNotExist:
            return False
    
    def generate_report(self, inspection_id: int) -> Optional[InspectionReportDTO]:
        """
        Generate report for an inspection.
        """
        try:
            inspection = RiskInspection.objects.get(
                id=inspection_id,
                tenant=self.tenant
            )
            return self._to_report_dto(inspection)
        except RiskInspection.DoesNotExist:
            return None
    
    def _update_overall_risk(self, inspection: RiskInspection):
        """
        Update overall risk level based on findings.
        """
        findings = inspection.findings.all()
        if not findings:
            inspection.overall_risk_level = 'low'
        else:
            # Set overall risk to highest finding risk
            risk_order = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
            max_risk = max(findings, key=lambda f: risk_order.get(f.risk_level, 0))
            inspection.overall_risk_level = max_risk.risk_level
        
        inspection.save()
    
    def _to_report_dto(self, inspection: RiskInspection) -> InspectionReportDTO:
        """
        Convert inspection to report DTO.
        """
        findings = inspection.findings.all()
        high_risk_count = findings.filter(risk_level__in=['high', 'critical']).count()
        
        # Calculate total estimated cost
        total_cost = sum(
            f.estimated_cost or 0
            for f in findings
        )
        
        return InspectionReportDTO(
            id=inspection.id,
            site_name=inspection.site_name,
            inspection_date=inspection.inspection_date,
            overall_risk_level=inspection.overall_risk_level or 'low',
            findings_count=findings.count(),
            high_risk_count=high_risk_count,
            estimated_total_cost=float(total_cost)
        )