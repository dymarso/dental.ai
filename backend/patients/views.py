from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Patient
from .serializers import PatientSerializer, PatientListSerializer


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing patients
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'is_active', 'preferred_contact_method', 'is_deleted']
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'patient_number']
    ordering_fields = ['last_name', 'first_name', 'created_at', 'date_of_birth']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Allow filtering to include deleted patients if requested"""
        queryset = Patient.objects.all()
        include_deleted = self.request.query_params.get('include_deleted', 'false').lower() == 'true'
        
        if include_deleted:
            queryset = Patient.objects.all_with_deleted()
        
        return queryset
    
    def get_serializer_class(self):
        """Use simplified serializer for list view"""
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer
    
    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        """Soft delete a patient"""
        patient = self.get_object()
        patient.soft_delete()
        return Response({
            'message': 'Paciente eliminado exitosamente',
            'patient': PatientSerializer(patient).data
        })
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a soft-deleted patient"""
        patient = self.get_object()
        patient.restore()
        return Response({
            'message': 'Paciente restaurado exitosamente',
            'patient': PatientSerializer(patient).data
        })
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get patient summary with related data"""
        patient = self.get_object()
        
        # Get related data counts
        treatments_count = patient.treatments.count()
        active_treatments = patient.treatments.filter(status='in_progress').count()
        appointments_count = patient.appointments.count()
        upcoming_appointments = patient.appointments.filter(
            date__gte=timezone.now().date(),
            status__in=['pending', 'confirmed']
        ).count()
        total_debt = sum(
            treatment.pending_balance 
            for treatment in patient.treatments.filter(status__in=['in_progress', 'with_debt'])
        )
        
        return Response({
            'patient': PatientSerializer(patient).data,
            'summary': {
                'treatments_count': treatments_count,
                'active_treatments': active_treatments,
                'appointments_count': appointments_count,
                'upcoming_appointments': upcoming_appointments,
                'total_debt': total_debt,
            }
        })


from django.utils import timezone
