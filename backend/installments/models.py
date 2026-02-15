from django.db import models
from patients.models import Patient
from budgets.models import Budget


class InstallmentPlan(models.Model):
    """Plan de cuotas para un presupuesto o tratamiento"""
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
        ('delinquent', 'Moroso'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='installment_plans',
        verbose_name='Paciente'
    )
    budget = models.ForeignKey(
        Budget,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='installment_plans',
        verbose_name='Presupuesto'
    )
    
    # Plan Details
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto Total'
    )
    number_of_installments = models.PositiveIntegerField(
        verbose_name='Número de Cuotas'
    )
    installment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto por Cuota'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Estado'
    )
    
    # Dates
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Plan de Cuotas'
        verbose_name_plural = 'Planes de Cuotas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['status', 'start_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.number_of_installments} cuotas"
    
    @property
    def paid_amount(self):
        """Total amount paid"""
        return sum(payment.amount for payment in self.payments.filter(status='paid'))
    
    @property
    def pending_amount(self):
        """Remaining amount to be paid"""
        return self.total_amount - self.paid_amount
    
    @property
    def paid_installments(self):
        """Number of installments paid"""
        return self.payments.filter(status='paid').count()
    
    @property
    def pending_installments(self):
        """Number of installments pending"""
        return self.number_of_installments - self.paid_installments
    
    @property
    def is_delinquent(self):
        """Check if there are overdue payments"""
        from django.utils import timezone
        return self.payments.filter(
            status='pending',
            due_date__lt=timezone.now().date()
        ).exists()


class InstallmentPayment(models.Model):
    """Individual installment payment"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('overdue', 'Vencido'),
        ('cancelled', 'Cancelado'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('transfer', 'Transferencia'),
        ('check', 'Cheque'),
    ]
    
    installment_plan = models.ForeignKey(
        InstallmentPlan,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Plan de Cuotas'
    )
    
    # Payment Details
    installment_number = models.PositiveIntegerField(
        verbose_name='Número de Cuota'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto'
    )
    
    # Dates
    due_date = models.DateField(verbose_name='Fecha de Vencimiento')
    payment_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha de Pago'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Payment Information
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        blank=True,
        null=True,
        verbose_name='Método de Pago'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Pago de Cuota'
        verbose_name_plural = 'Pagos de Cuotas'
        ordering = ['installment_number']
        indexes = [
            models.Index(fields=['installment_plan', 'status']),
            models.Index(fields=['due_date', 'status']),
        ]
        unique_together = [['installment_plan', 'installment_number']]
    
    def __str__(self):
        return f"Cuota {self.installment_number} - {self.installment_plan.patient.full_name}"
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        from django.utils import timezone
        if self.status == 'pending':
            return self.due_date < timezone.now().date()
        return False
    
    @property
    def days_overdue(self):
        """Number of days overdue"""
        from django.utils import timezone
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
