from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum
from django.utils import timezone
from .models import Payment, Expense
from .serializers import PaymentSerializer, ExpenseSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('patient', 'treatment')
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'treatment', 'payment_method', 'payment_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'reference_number']
    ordering = ['-payment_date']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get payment summary"""
        today = timezone.now().date()
        
        # Daily total
        daily_total = self.queryset.filter(payment_date=today).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Monthly total
        monthly_total = self.queryset.filter(
            payment_date__year=today.year,
            payment_date__month=today.month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'daily_total': daily_total,
            'monthly_total': monthly_total,
        })


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'payment_method', 'expense_date']
    search_fields = ['description', 'supplier', 'invoice_number']
    ordering = ['-expense_date']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get expense summary"""
        today = timezone.now().date()
        
        # Daily total
        daily_total = self.queryset.filter(expense_date=today).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Monthly total
        monthly_total = self.queryset.filter(
            expense_date__year=today.year,
            expense_date__month=today.month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # By category (monthly)
        by_category = self.queryset.filter(
            expense_date__year=today.year,
            expense_date__month=today.month
        ).values('category').annotate(total=Sum('amount'))
        
        return Response({
            'daily_total': daily_total,
            'monthly_total': monthly_total,
            'by_category': by_category,
        })
