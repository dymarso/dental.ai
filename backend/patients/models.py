from django.db import models
from django.core.validators import EmailValidator, RegexValidator


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
    
    # Additional Information
    notes = models.TextField(blank=True, null=True, verbose_name='Notas Generales')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
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
