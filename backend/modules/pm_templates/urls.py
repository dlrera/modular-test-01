"""
PM Template module URL configuration.
"""
from rest_framework.routers import DefaultRouter
from .views import PMTemplateViewSet

router = DefaultRouter()
router.register('pm-templates', PMTemplateViewSet, basename='pmtemplate')

urlpatterns = router.urls