from django.shortcuts import render

from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import MedicalHistory, ClinicalNote, ClinicalFile, Odontogram, Periodontogram
from .serializers import (
    MedicalHistorySerializer,
    ClinicalNoteSerializer,
    ClinicalFileSerializer,
    OdontogramSerializer,
    PeriodontogramSerializer
)


class MedicalHistoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing medical histories"""
    queryset = MedicalHistory.objects.all()
    serializer_class = MedicalHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['patient']
    search_fields = ['patient__first_name', 'patient__last_name', 'chronic_diseases', 'allergies']


class ClinicalNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for managing clinical notes"""
    queryset = ClinicalNote.objects.select_related('patient')
    serializer_class = ClinicalNoteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'date']
    search_fields = ['title', 'description', 'observations', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date', '-created_at']


class ClinicalFileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing clinical files"""
    queryset = ClinicalFile.objects.select_related('patient')
    serializer_class = ClinicalFileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'file_type', 'clinical_note']
    search_fields = ['title', 'description', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['date_taken', 'uploaded_at']
    ordering = ['-date_taken', '-uploaded_at']


class OdontogramViewSet(viewsets.ModelViewSet):
    """ViewSet for managing odontograms"""
    queryset = Odontogram.objects.select_related('patient')
    serializer_class = OdontogramSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'date']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']


class PeriodontogramViewSet(viewsets.ModelViewSet):
    """ViewSet for managing periodontograms"""
    queryset = Periodontogram.objects.select_related('patient')
    serializer_class = PeriodontogramSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['patient', 'date', 'has_abnormal_values']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date']

