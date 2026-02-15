from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import InstallmentPlan, InstallmentPayment
from .serializers import (
    InstallmentPlanSerializer,
    InstallmentPlanCreateSerializer,
    InstallmentPaymentSerializer
)


class InstallmentPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing installment plans
    """
    queryset = InstallmentPlan.objects.select_related('patient', 'budget').prefetch_related('payments')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'status', 'budget']
    search_fields = ['patient__first_name', 'patient__last_name']
    ordering_fields = ['start_date', 'total_amount', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return InstallmentPlanCreateSerializer
        return InstallmentPlanSerializer
    
    @action(detail=False, methods=['get'])
    def delinquent(self, request):
        """Get all delinquent installment plans"""
        today = timezone.now().date()
        
        # Get plans with overdue payments
        delinquent_plans = []
        for plan in self.queryset.filter(status='active'):
            if plan.is_delinquent:
                delinquent_plans.append(plan)
        
        serializer = self.get_serializer(delinquent_plans, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_delinquent(self, request, pk=None):
        """Mark a plan as delinquent"""
        plan = self.get_object()
        plan.status = 'delinquent'
        plan.save()
        
        serializer = self.get_serializer(plan)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an installment plan"""
        plan = self.get_object()
        
        if plan.status == 'completed':
            return Response(
                {'error': 'No se puede cancelar un plan completado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        plan.status = 'cancelled'
        plan.save()
        
        # Cancel all pending payments
        plan.payments.filter(status='pending').update(status='cancelled')
        
        serializer = self.get_serializer(plan)
        return Response(serializer.data)


class InstallmentPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing installment payments
    """
    queryset = InstallmentPayment.objects.select_related('installment_plan', 'installment_plan__patient')
    serializer_class = InstallmentPaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['installment_plan', 'status', 'payment_method']
    search_fields = ['installment_plan__patient__first_name', 'installment_plan__patient__last_name']
    ordering_fields = ['due_date', 'payment_date', 'installment_number']
    ordering = ['due_date']
    
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark a payment as paid"""
        payment = self.get_object()
        
        if payment.status == 'paid':
            return Response(
                {'error': 'El pago ya está marcado como pagado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        payment_method = request.data.get('payment_method', 'cash')
        payment_date = request.data.get('payment_date', timezone.now().date())
        notes = request.data.get('notes', '')
        
        payment.status = 'paid'
        payment.payment_method = payment_method
        payment.payment_date = payment_date
        payment.notes = notes
        payment.save()
        
        # Check if all payments are completed
        plan = payment.installment_plan
        if plan.payments.filter(status='pending').count() == 0:
            plan.status = 'completed'
            plan.save()
        
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue payments"""
        today = timezone.now().date()
        overdue_payments = self.queryset.filter(
            status='pending',
            due_date__lt=today
        )
        
        serializer = self.get_serializer(overdue_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming payments (next 30 days)"""
        from datetime import timedelta
        today = timezone.now().date()
        upcoming_date = today + timedelta(days=30)
        
        upcoming_payments = self.queryset.filter(
            status='pending',
            due_date__gte=today,
            due_date__lte=upcoming_date
        )
        
        serializer = self.get_serializer(upcoming_payments, many=True)
        return Response(serializer.data)
