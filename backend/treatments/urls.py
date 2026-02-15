from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TreatmentViewSet,
    TreatmentProgressViewSet,
    TreatmentFileViewSet,
    OrthodonticCaseViewSet,
    AestheticProcedureViewSet
)

router = DefaultRouter()
router.register(r'', TreatmentViewSet, basename='treatment')
router.register(r'progress', TreatmentProgressViewSet, basename='treatment-progress')
router.register(r'files', TreatmentFileViewSet, basename='treatment-file')
router.register(r'orthodontic-cases', OrthodonticCaseViewSet, basename='orthodontic-case')
router.register(r'aesthetic-procedures', AestheticProcedureViewSet, basename='aesthetic-procedure')

urlpatterns = router.urls

