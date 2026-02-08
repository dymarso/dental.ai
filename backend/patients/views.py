from rest_framework import viewsets, filters
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
    filterset_fields = ['gender', 'is_active', 'preferred_contact_method']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    ordering_fields = ['last_name', 'first_name', 'created_at', 'date_of_birth']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use simplified serializer for list view"""
        if self.action == 'list':
            return PatientListSerializer
        return PatientSerializer
    
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
