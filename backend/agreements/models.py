from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient


class Agreement(models.Model):
    """Agreement/Consent form model with digital signature support"""
    
    TYPE_CHOICES = [
        ('informed_consent', 'Consentimiento Informado'),
        ('treatment_plan', 'Plan de Tratamiento'),
        ('privacy_policy', 'Política de Privacidad'),
        ('financial_agreement', 'Acuerdo Financiero'),
        ('anesthesia_consent', 'Consentimiento para Anestesia'),
        ('x_ray_consent', 'Consentimiento para Radiografías'),
        ('general', 'General'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('signed', 'Firmado'),
        ('declined', 'Rechazado'),
        ('expired', 'Expirado'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='agreements',
        verbose_name='Paciente'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_agreements',
        verbose_name='Creado por'
    )
    
    # Agreement Details
    agreement_type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        verbose_name='Tipo de Acuerdo'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    content = models.TextField(
        verbose_name='Contenido del Acuerdo'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Signature
    signature_data = models.TextField(
        blank=True,
        null=True,
        verbose_name='Datos de Firma Digital',
        help_text='Base64 encoded signature image'
    )
    signed_by_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Firmado por (nombre)'
    )
    signed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Firma'
    )
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name='Dirección IP de Firma'
    )
    
    # Dates
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Expiración'
    )
    
    # PDF Storage
    pdf_file = models.FileField(
        upload_to='agreements/pdfs/',
        blank=True,
        null=True,
        verbose_name='Archivo PDF'
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
        verbose_name = 'Acuerdo'
        verbose_name_plural = 'Acuerdos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['agreement_type', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.patient.full_name} ({self.status})"
    
    @property
    def is_signed(self):
        """Check if agreement is signed"""
        return self.status == 'signed' and self.signature_data is not None
    
    @property
    def is_expired(self):
        """Check if agreement is expired"""
        from django.utils import timezone
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
