from django.db import models
from patients.models import Patient
from installments.models import InstallmentPayment


class OnlinePayment(models.Model):
    """Online payment model for tracking payment transactions"""
    
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Tarjeta de Crédito/Débito'),
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('mercadopago', 'MercadoPago'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('processing', 'Procesando'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
        ('cancelled', 'Cancelado'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='online_payments',
        verbose_name='Paciente'
    )
    installment_payment = models.ForeignKey(
        InstallmentPayment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='online_payments',
        verbose_name='Pago de Cuota'
    )
    
    # Payment Details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Monto'
    )
    currency = models.CharField(
        max_length=3,
        default='MXN',
        verbose_name='Moneda'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Método de Pago'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Payment Gateway Information
    transaction_id = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='ID de Transacción'
    )
    gateway_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Respuesta del Gateway'
    )
    
    # Dates
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Pago'
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Completado el'
    )
    
    # Customer Information
    customer_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email del Cliente'
    )
    customer_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Nombre del Cliente'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensaje de Error'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Pago en Línea'
        verbose_name_plural = 'Pagos en Línea'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['status', 'payment_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - ${self.amount} ({self.status})"


class StripePayment(models.Model):
    """Extended model for Stripe-specific payment information"""
    
    online_payment = models.OneToOneField(
        OnlinePayment,
        on_delete=models.CASCADE,
        related_name='stripe_details',
        verbose_name='Pago en Línea'
    )
    
    # Stripe-specific fields
    stripe_payment_intent_id = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Stripe Payment Intent ID'
    )
    stripe_customer_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Stripe Customer ID'
    )
    stripe_charge_id = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Stripe Charge ID'
    )
    
    # Card Information (last 4 digits only)
    card_brand = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Marca de Tarjeta'
    )
    card_last4 = models.CharField(
        max_length=4,
        blank=True,
        null=True,
        verbose_name='Últimos 4 dígitos'
    )
    card_exp_month = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Mes de Expiración'
    )
    card_exp_year = models.IntegerField(
        blank=True,
        null=True,
        verbose_name='Año de Expiración'
    )
    
    # Metadata
    stripe_metadata = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Metadata de Stripe'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Pago Stripe'
        verbose_name_plural = 'Pagos Stripe'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Stripe - {self.stripe_payment_intent_id}"
