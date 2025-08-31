"""
Risk inspection module URL configuration.
"""
from rest_framework.routers import DefaultRouter
from .views import RiskInspectionViewSet

router = DefaultRouter()
router.register('risk-inspections', RiskInspectionViewSet, basename='riskinspection')

urlpatterns = router.urls