from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Budget, BudgetItem
from .serializers import BudgetSerializer, BudgetItemSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.select_related('patient').prefetch_related('items')
    serializer_class = BudgetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'status']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    ordering = ['-created_date']
    
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


from django.utils import timezone
