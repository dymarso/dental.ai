from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Budget, BudgetItem
from .serializers import BudgetSerializer, BudgetItemSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.select_related('patient').prefetch_related('items')
    serializer_class = BudgetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'status', 'version']
    search_fields = ['title', 'patient__first_name', 'patient__last_name', 'budget_number']
    ordering = ['-created_date']
    
    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """Create a new version of the budget"""
        budget = self.get_object()
        
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user.username
        
        new_budget = budget.create_new_version(user=user)
        
        return Response({
            'message': 'Nueva versión creada exitosamente',
            'budget': BudgetSerializer(new_budget).data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def generate_pdf(self, request, pk=None):
        """Generate and download PDF for the budget"""
        budget = self.get_object()
        
        try:
            pdf = budget.generate_pdf()
            
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="presupuesto_{budget.budget_number}.pdf"'
            
            return response
        except Exception as e:
            return Response(
                {'error': f'Error generando PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def convert_to_treatment(self, request, pk=None):
        """Convert budget to treatment"""
        budget = self.get_object()
        
        if budget.status == 'converted':
            return Response(
                {'error': 'Budget already converted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import here to avoid circular import
        from treatments.models import Treatment
        
        # Create treatment from budget
        treatment = Treatment.objects.create(
            patient=budget.patient,
            treatment_type=budget.title,
            dentist_responsible=budget.created_by or 'N/A',
            start_date=timezone.now().date(),
            total_sessions=1,
            total_price=budget.total_amount,
            description=budget.description,
            status='in_progress'
        )
        
        # Update budget status
        budget.status = 'converted'
        budget.save()
        
        return Response({
            'message': 'Budget converted to treatment successfully',
            'treatment_id': treatment.id
        })


class BudgetItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing budget items"""
    queryset = BudgetItem.objects.select_related('budget')
    serializer_class = BudgetItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['budget']
    ordering_fields = ['order']
    ordering = ['order']

