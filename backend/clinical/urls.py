from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MedicalHistoryViewSet,
    ClinicalNoteViewSet,
    ClinicalFileViewSet,
    OdontogramViewSet,
    PeriodontogramViewSet
)

router = DefaultRouter()
router.register(r'medical-histories', MedicalHistoryViewSet)
router.register(r'clinical-notes', ClinicalNoteViewSet)
router.register(r'clinical-files', ClinicalFileViewSet)
router.register(r'odontograms', OdontogramViewSet)
router.register(r'periodontograms', PeriodontogramViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
