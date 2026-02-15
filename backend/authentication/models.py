from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class RefreshToken(models.Model):
    """Model to store refresh tokens for JWT authentication"""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='refresh_tokens',
        verbose_name='Usuario'
    )
    token = models.CharField(
        max_length=500,
        unique=True,
        verbose_name='Token'
    )
    jti = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        verbose_name='JWT ID'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    expires_at = models.DateTimeField(
        verbose_name='Fecha de Expiración'
    )
    revoked = models.BooleanField(
        default=False,
        verbose_name='Revocado'
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Revocación'
    )
    
    class Meta:
        verbose_name = 'Token de Refresco'
        verbose_name_plural = 'Tokens de Refresco'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'revoked']),
            models.Index(fields=['token']),
            models.Index(fields=['jti']),
        ]
    
    def __str__(self):
        return f"Token for {self.user.username} - {self.created_at}"
    
    @property
    def is_expired(self):
        """Check if token is expired"""
        return timezone.now() > self.expires_at
    
    def revoke(self):
        """Revoke this token"""
        self.revoked = True
        self.revoked_at = timezone.now()
        self.save()


class AuditLog(models.Model):
    """Audit log for tracking access to patient records and sensitive operations"""
    
    ACTION_CHOICES = [
        ('view', 'Ver'),
        ('create', 'Crear'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('login', 'Iniciar Sesión'),
        ('logout', 'Cerrar Sesión'),
        ('failed_login', 'Intento de Inicio de Sesión Fallido'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Usuario'
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Nombre de Usuario',
        help_text='Stored separately in case user is deleted'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Acción'
    )
    resource_type = models.CharField(
        max_length=100,
        verbose_name='Tipo de Recurso',
        help_text='E.g., Patient, Appointment, ClinicalRecord'
    )
    resource_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID del Recurso'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP'
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name='User Agent'
    )
    details = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Detalles'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.action} - {self.resource_type} - {self.timestamp}"
