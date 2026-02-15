from django.db import models
from patients.models import Patient
from appointments.models import Appointment


class Notification(models.Model):
    """Notification model for sending messages to patients"""
    
    TYPE_CHOICES = [
        ('appointment_reminder', 'Recordatorio de Cita'),
        ('appointment_confirmation', 'Confirmación de Cita'),
        ('payment_reminder', 'Recordatorio de Pago'),
        ('treatment_update', 'Actualización de Tratamiento'),
        ('general', 'General'),
    ]
    
    METHOD_CHOICES = [
        ('email', 'Correo Electrónico'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviado'),
        ('failed', 'Fallido'),
        ('delivered', 'Entregado'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Paciente'
    )
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
        verbose_name='Cita'
    )
    
    # Notification Details
    notification_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        verbose_name='Tipo de Notificación'
    )
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        verbose_name='Método de Envío'
    )
    
    # Message
    subject = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Asunto'
    )
    message = models.TextField(verbose_name='Mensaje')
    
    # Recipient
    recipient_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Email del Destinatario'
    )
    recipient_phone = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name='Teléfono del Destinatario'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Scheduling
    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Programado para'
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Enviado el'
    )
    
    # Response
    response_data = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Datos de Respuesta'
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
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['notification_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.patient.full_name} ({self.status})"
