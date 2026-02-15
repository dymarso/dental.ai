from django.db import models
from django.core.validators import EmailValidator, RegexValidator
from django.utils import timezone
import uuid
from datetime import datetime


class PatientManager(models.Manager):
    """Custom manager for Patient model with soft delete support"""
    
    def get_queryset(self):
        """Override queryset to exclude soft-deleted patients by default"""
        return super().get_queryset().filter(is_deleted=False)
    
    def all_with_deleted(self):
        """Return all patients including soft-deleted ones"""
        return super().get_queryset()
    
    def deleted_only(self):
        """Return only soft-deleted patients"""
        return super().get_queryset().filter(is_deleted=True)


class Patient(models.Model):
    """Patient model for managing patient information"""
    
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    CONTACT_METHOD_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('email', 'Correo Electrónico'),
    ]
    
    # UUID and Patient Number
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name='UUID'
    )
    patient_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name='Número de Paciente',
        help_text='Formato: PAT-YYYYMMDD-XXXX'
    )
    
    # Basic Information
    first_name = models.CharField(max_length=100, verbose_name='Nombre')
    last_name = models.CharField(max_length=100, verbose_name='Apellidos')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='Género')
    date_of_birth = models.DateField(verbose_name='Fecha de Nacimiento')
    
    # Contact Information
    phone_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Número de teléfono debe estar en formato: '+999999999'. Hasta 15 dígitos permitidos."
    )
    phone = models.CharField(
        validators=[phone_validator],
        max_length=17,
        verbose_name='Teléfono'
    )
    email = models.EmailField(
        validators=[EmailValidator()],
        blank=True,
        null=True,
        verbose_name='Correo Electrónico'
    )
    preferred_contact_method = models.CharField(
        max_length=10,
        choices=CONTACT_METHOD_CHOICES,
        default='whatsapp',
        verbose_name='Método de Confirmación Preferido'
    )
    
    # Emergency Contact Information
    emergency_contact_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Nombre del Contacto de Emergencia'
    )
    emergency_contact_phone = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name='Teléfono del Contacto de Emergencia'
    )
    emergency_contact_relationship = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Relación con el Contacto de Emergencia',
        help_text='Ej: Madre, Padre, Esposo/a, Hermano/a, etc.'
    )
    
    # Additional Information
    notes = models.TextField(blank=True, null=True, verbose_name='Notas Generales')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    # Soft Delete
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    deleted_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Eliminación'
    )
    
    # Custom Manager
    objects = PatientManager()
    
    class Meta:
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.last_name}, {self.first_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    @property
    def whatsapp_link(self):
        """Generate WhatsApp link for quick messaging"""
        # Remove non-numeric characters
        clean_phone = ''.join(filter(str.isdigit, self.phone))
        return f"https://wa.me/{clean_phone}"
    
    def save(self, *args, **kwargs):
        """Override save to generate patient_number if not exists"""
        if not self.patient_number:
            self.patient_number = self._generate_patient_number()
        super().save(*args, **kwargs)
    
    def _generate_patient_number(self):
        """Generate unique patient number in format PAT-YYYYMMDD-XXXX"""
        from django.utils import timezone
        today = timezone.now()
        date_str = today.strftime('%Y%m%d')
        
        # Get the count of patients created today
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Use all_with_deleted to ensure we don't have duplicate numbers
        count = Patient.objects.all_with_deleted().filter(
            created_at__range=[today_start, today_end]
        ).count()
        
        # Generate sequential number
        sequence = str(count + 1).zfill(4)
        return f"PAT-{date_str}-{sequence}"
    
    def soft_delete(self):
        """Soft delete the patient"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restore a soft-deleted patient"""
        self.is_deleted = False
        self.deleted_at = None
        self.is_active = True
        self.save()
