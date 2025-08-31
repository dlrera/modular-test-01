"""
PM Template service layer.
"""
from dataclasses import dataclass
from typing import List, Optional
from .models import PMTemplate


@dataclass
class PMTemplateCreateDTO:
    """DTO for creating PM template."""
    name: str
    description: str
    category: str
    frequency: str
    tasks: List[dict]
    ai_prompt: str = ""


@dataclass 
class PMTemplateDTO:
    """DTO for PM template data."""
    id: int
    name: str
    category: str
    frequency: str
    task_count: int
    is_active: bool


class PMTemplateService:
    """
    Service class for PM template operations.
    """
    
    def __init__(self, user, tenant):
        self.user = user
        self.tenant = tenant
    
    def create_template(self, dto: PMTemplateCreateDTO) -> PMTemplateDTO:
        """
        Create a new PM template.
        """
        template = PMTemplate.objects.create(
            tenant=self.tenant,
            created_by=self.user,
            name=dto.name,
            description=dto.description,
            category=dto.category,
            frequency=dto.frequency,
            tasks=dto.tasks,
            ai_generated=bool(dto.ai_prompt),
            ai_prompt=dto.ai_prompt
        )
        
        return self._to_dto(template)
    
    def generate_from_ai(self, prompt: str) -> PMTemplateDTO:
        """
        Generate PM template from AI prompt.
        TODO: Integrate with AI service.
        """
        # Placeholder for AI integration
        # For now, create a sample template
        sample_tasks = [
            {"name": "Check equipment", "description": "Inspect for wear"},
            {"name": "Clean components", "description": "Remove debris"},
            {"name": "Test operation", "description": "Verify functionality"}
        ]
        
        dto = PMTemplateCreateDTO(
            name=f"AI Generated: {prompt[:50]}",
            description=f"Template generated from prompt: {prompt}",
            category="General",
            frequency="monthly",
            tasks=sample_tasks,
            ai_prompt=prompt
        )
        
        return self.create_template(dto)
    
    def list_templates(self, category: Optional[str] = None) -> List[PMTemplateDTO]:
        """
        List PM templates.
        """
        queryset = PMTemplate.objects.filter(
            tenant=self.tenant,
            is_active=True
        )
        
        if category:
            queryset = queryset.filter(category=category)
        
        return [self._to_dto(template) for template in queryset]
    
    def _to_dto(self, template: PMTemplate) -> PMTemplateDTO:
        """
        Convert PMTemplate model to DTO.
        """
        return PMTemplateDTO(
            id=template.id,
            name=template.name,
            category=template.category,
            frequency=template.frequency,
            task_count=len(template.tasks) if template.tasks else 0,
            is_active=template.is_active
        )