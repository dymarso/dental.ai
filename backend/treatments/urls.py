from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TreatmentViewSet, TreatmentProgressViewSet, TreatmentFileViewSet

router = DefaultRouter()
router.register(r'', TreatmentViewSet, basename='treatment')
router.register(r'progress', TreatmentProgressViewSet, basename='treatment-progress')
router.register(r'files', TreatmentFileViewSet, basename='treatment-file')

urlpatterns = router.urls
