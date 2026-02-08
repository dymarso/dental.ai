from django.db import models
from patients.models import Patient


class Budget(models.Model):
    """Budget/Quote model for treatment proposals"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('converted', 'Convertido a Tratamiento'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Paciente'
    )
    
    # Budget Details
    title = models.CharField(
        max_length=200,
        verbose_name='Título del Presupuesto'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción General'
    )
    
    # Dates
    created_date = models.DateField(auto_now_add=True, verbose_name='Fecha de Creación')
    valid_until = models.DateField(
        blank=True,
        null=True,
        verbose_name='Válido Hasta'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Total
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Monto Total'
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
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.title} - {self.patient.full_name}"
    
    def calculate_total(self):
        """Calculate total from all budget items"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        return total


class BudgetItem(models.Model):
    """Individual items in a budget"""
    
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Presupuesto'
    )
    
    # Item Details
    treatment_type = models.CharField(
        max_length=200,
        verbose_name='Tipo de Tratamiento'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    
    # Pricing
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Unitario'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal'
    )
    
    # Metadata
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden'
    )
    
    class Meta:
        verbose_name = 'Item de Presupuesto'
        verbose_name_plural = 'Items de Presupuesto'
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.treatment_type} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate subtotal before saving"""
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
