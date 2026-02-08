from django.db import models
from django.contrib.auth.models import User


class DoctorProfile(models.Model):
    """Doctor/Dentist profile model"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        verbose_name='Usuario'
    )
    
    # Personal Information
    full_name = models.CharField(
        max_length=200,
        verbose_name='Nombre Completo'
    )
    specialty = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Especialidad'
    )
    professional_license = models.CharField(
        max_length=100,
        verbose_name='Cédula Profesional'
    )
    
    # Contact Information
    phone = models.CharField(
        max_length=17,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Correo Electrónico'
    )
    
    # Clinic Information
    clinic_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Nombre del Consultorio'
    )
    clinic_address = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección del Consultorio'
    )
    
    # Digital Assets
    digital_signature = models.ImageField(
        upload_to='signatures/',
        blank=True,
        null=True,
        verbose_name='Firma Digital'
    )
    clinic_logo = models.ImageField(
        upload_to='logos/',
        blank=True,
        null=True,
        verbose_name='Logo del Consultorio'
    )
    
    # Additional Information
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='Biografía'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Perfil de Doctor'
        verbose_name_plural = 'Perfiles de Doctores'
    
    def __str__(self):
        return self.full_name
