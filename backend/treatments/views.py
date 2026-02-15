from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Treatment, TreatmentProgress, TreatmentFile, OrthodonticCase, AestheticProcedure
from .serializers import (
    TreatmentSerializer,
    TreatmentListSerializer,
    TreatmentProgressSerializer,
    TreatmentFileSerializer,
    OrthodonticCaseSerializer,
    AestheticProcedureSerializer
)


class TreatmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing treatments
    """
    queryset = Treatment.objects.select_related('patient').prefetch_related('progress_records')
    serializer_class = TreatmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'status', 'dentist_responsible']
    search_fields = ['treatment_type', 'patient__first_name', 'patient__last_name']
    ordering_fields = ['start_date', 'end_date', 'total_price', 'status']
    ordering = ['-start_date']
    
    def get_serializer_class(self):
        """Use simplified serializer for list view"""
        if self.action == 'list':
            return TreatmentListSerializer
        return TreatmentSerializer
    
    @action(detail=True, methods=['post'])
    def add_progress(self, request, pk=None):
        """Add progress record to treatment"""
        treatment = self.get_object()
        data = request.data.copy()
        data['treatment'] = treatment.id
        
        serializer = TreatmentProgressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Update completed sessions
            if request.data.get('mark_session_complete'):
                treatment.completed_sessions += 1
                treatment.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        """Add payment to treatment"""
        treatment = self.get_object()
        amount = request.data.get('amount', 0)
        
        try:
            amount = float(amount)
            treatment.amount_paid += amount
            
            # Update status if fully paid
            if treatment.is_paid and treatment.status != 'completed':
                treatment.status = 'in_progress'
            
            treatment.save()
            return Response({
                'message': 'Payment added successfully',
                'treatment': TreatmentSerializer(treatment).data
            })
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )


class TreatmentProgressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing treatment progress records
    """
    queryset = TreatmentProgress.objects.select_related('treatment').prefetch_related('files')
    serializer_class = TreatmentProgressSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['treatment']
    ordering_fields = ['date', 'session_number']
    ordering = ['-date']


class TreatmentFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing treatment files
    """
    queryset = TreatmentFile.objects.select_related('progress')
    serializer_class = TreatmentFileSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['progress', 'file_type']
    ordering = ['-uploaded_at']


class OrthodonticCaseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orthodontic cases"""
    queryset = OrthodonticCase.objects.select_related('treatment', 'treatment__patient')
    serializer_class = OrthodonticCaseSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['treatment', 'appliance_type']
    ordering_fields = ['start_date', 'expected_end_date']
    ordering = ['-start_date']
    
    @action(detail=True, methods=['post'])
    def add_adjustment(self, request, pk=None):
        """Add an adjustment to the orthodontic case"""
        case = self.get_object()
        
        date = request.data.get('date')
        description = request.data.get('description')
        performed_by = request.data.get('performed_by')
        
        if not date or not description:
            return Response(
                {'error': 'Se requieren los campos "date" y "description"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        case.add_adjustment(date, description, performed_by)
        
        return Response({
            'message': 'Ajuste agregado exitosamente',
            'case': OrthodonticCaseSerializer(case).data
        })


class AestheticProcedureViewSet(viewsets.ModelViewSet):
    """ViewSet for managing aesthetic procedures"""
    queryset = AestheticProcedure.objects.select_related('treatment', 'treatment__patient')
    serializer_class = AestheticProcedureSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['treatment', 'procedure_type', 'satisfaction_rating']
    ordering_fields = ['completion_date', 'created_at']
    ordering = ['-completion_date', '-created_at']

