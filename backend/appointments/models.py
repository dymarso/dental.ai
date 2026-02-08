from django.db import models
from patients.models import Patient


class Appointment(models.Model):
    """Appointment/Calendar model for scheduling patient appointments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Completada'),
        ('no_show', 'No Asistió'),
    ]
    
    CONSULTATION_TYPE_CHOICES = [
        ('first_visit', 'Primera Visita'),
        ('follow_up', 'Seguimiento'),
        ('cleaning', 'Limpieza'),
        ('extraction', 'Extracción'),
        ('filling', 'Empaste'),
        ('root_canal', 'Endodoncia'),
        ('orthodontics', 'Ortodoncia'),
        ('implant', 'Implante'),
        ('emergency', 'Emergencia'),
        ('other', 'Otro'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Paciente'
    )
    
    # Appointment Details
    consultation_type = models.CharField(
        max_length=50,
        choices=CONSULTATION_TYPE_CHOICES,
        verbose_name='Tipo de Consulta'
    )
    date = models.DateField(verbose_name='Fecha')
    start_time = models.TimeField(verbose_name='Hora de Inicio')
    end_time = models.TimeField(verbose_name='Hora de Fin')
    
    # Facility
    dental_unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Unidad/Sillón',
        help_text='Ej: Sillón 1, Sillón 2, etc.'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Notes
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Reminders
    reminder_sent = models.BooleanField(
        default=False,
        verbose_name='Recordatorio Enviado'
    )
    reminder_sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Recordatorio Enviado el'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['date', 'start_time']
        indexes = [
            models.Index(fields=['date', 'start_time']),
            models.Index(fields=['patient', 'date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.date} {self.start_time}"
    
    @property
    def duration_minutes(self):
        """Calculate appointment duration in minutes"""
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)
        duration = end - start
        return int(duration.total_seconds() / 60)


class AppointmentReminder(models.Model):
    """Log of reminders sent for appointments"""
    
    REMINDER_METHOD_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('email', 'Correo Electrónico'),
    ]
    
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='reminders',
        verbose_name='Cita'
    )
    
    method = models.CharField(
        max_length=20,
        choices=REMINDER_METHOD_CHOICES,
        verbose_name='Método'
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='Enviado el')
    success = models.BooleanField(default=True, verbose_name='Exitoso')
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name='Mensaje de Error'
    )
    
    class Meta:
        verbose_name = 'Recordatorio de Cita'
        verbose_name_plural = 'Recordatorios de Citas'
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"Recordatorio {self.method} - {self.appointment}"
