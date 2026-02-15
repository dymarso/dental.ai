from django.db import models
from django.core.exceptions import ValidationError
from patients.models import Patient
from datetime import datetime, time, timedelta


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
    
    # Telemedicine
    telemedicine_enabled = models.BooleanField(
        default=False,
        verbose_name='Telemedicina Habilitada'
    )
    video_link = models.URLField(
        blank=True,
        null=True,
        verbose_name='Enlace de Video',
        help_text='Enlace para sesión de telemedicina (Zoom, Meet, etc.)'
    )
    
    # Public Booking
    public_booking = models.BooleanField(
        default=False,
        verbose_name='Reserva Pública',
        help_text='Indica si la cita fue reservada por el paciente vía sistema público'
    )
    
    # Creator tracking
    created_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Creado por',
        help_text='Usuario que creó la cita'
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
    
    def clean(self):
        """Validate appointment data"""
        super().clean()
        
        # Validate business hours (8 AM - 8 PM)
        if not self.is_within_business_hours():
            raise ValidationError(
                'Las citas deben ser entre las 8:00 AM y las 8:00 PM'
            )
        
        # Check for conflicts
        if self.has_conflicts():
            raise ValidationError(
                'Ya existe una cita en este horario para esta unidad dental'
            )
    
    def is_within_business_hours(self):
        """Check if appointment is within business hours (8 AM - 8 PM)"""
        business_start = time(8, 0)  # 8:00 AM
        business_end = time(20, 0)    # 8:00 PM
        
        return (
            self.start_time >= business_start and 
            self.end_time <= business_end and
            self.start_time < self.end_time
        )
    
    def has_conflicts(self):
        """Check for conflicting appointments"""
        # Build base queryset
        conflicts = Appointment.objects.filter(
            date=self.date,
            status__in=['pending', 'confirmed']
        )
        
        # Exclude current appointment if updating
        if self.pk:
            conflicts = conflicts.exclude(pk=self.pk)
        
        # If dental_unit is specified, check for conflicts on that unit
        if self.dental_unit:
            conflicts = conflicts.filter(dental_unit=self.dental_unit)
        
        # Check for time overlap
        for appt in conflicts:
            # Check if times overlap
            if (self.start_time < appt.end_time and self.end_time > appt.start_time):
                return True
        
        return False
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.full_clean()
        super().save(*args, **kwargs)


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
