from rest_framework.routers import DefaultRouter
from .views import (
    FolderViewSet, DocumentViewSet, 
    DocumentShareViewSet, ShareNotificationViewSet
)

router = DefaultRouter()
router.register('folders', FolderViewSet, basename='folder')
router.register('files', DocumentViewSet, basename='document')
router.register('shares', DocumentShareViewSet, basename='share')
router.register('notifications', ShareNotificationViewSet, basename='notification')

urlpatterns = router.urls