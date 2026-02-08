from django.db import models
from patients.models import Patient
from treatments.models import Treatment


class Payment(models.Model):
    """Payment model for tracking income from treatments"""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
        ('card', 'Tarjeta'),
        ('check', 'Cheque'),
        ('other', 'Otro'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='Paciente'
    )
    treatment = models.ForeignKey(
        Treatment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        verbose_name='Tratamiento'
    )
    
    # Payment Details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Método de Pago'
    )
    payment_date = models.DateField(verbose_name='Fecha de Pago')
    
    # Reference
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número de Referencia',
        help_text='Número de transferencia, voucher, etc.'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Metadata
    created_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Registrado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-payment_date', '-created_at']
        indexes = [
            models.Index(fields=['payment_date']),
            models.Index(fields=['patient', 'payment_date']),
        ]
    
    def __str__(self):
        return f"${self.amount} - {self.patient.full_name} ({self.payment_date})"


class Expense(models.Model):
    """Expense model for tracking clinic expenses"""
    
    CATEGORY_CHOICES = [
        ('materials', 'Materiales'),
        ('laboratory', 'Laboratorio'),
        ('rent', 'Renta'),
        ('salaries', 'Sueldos'),
        ('utilities', 'Servicios'),
        ('equipment', 'Equipo'),
        ('maintenance', 'Mantenimiento'),
        ('marketing', 'Marketing'),
        ('other', 'Otros'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
        ('card', 'Tarjeta'),
        ('check', 'Cheque'),
        ('other', 'Otro'),
    ]
    
    # Expense Details
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name='Categoría'
    )
    description = models.CharField(
        max_length=200,
        verbose_name='Descripción'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto'
    )
    expense_date = models.DateField(verbose_name='Fecha del Gasto')
    
    # Payment
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Método de Pago'
    )
    
    # Supplier/Provider
    supplier = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Proveedor'
    )
    
    # Reference
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Número de Factura'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Metadata
    created_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Registrado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Gasto'
        verbose_name_plural = 'Gastos'
        ordering = ['-expense_date', '-created_at']
        indexes = [
            models.Index(fields=['expense_date']),
            models.Index(fields=['category', 'expense_date']),
        ]
    
    def __str__(self):
        return f"${self.amount} - {self.description} ({self.expense_date})"
