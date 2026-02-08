from django.db import models
from patients.models import Patient


class Treatment(models.Model):
    """Treatment model for managing dental treatments"""
    
    STATUS_CHOICES = [
        ('in_progress', 'En Curso'),
        ('completed', 'Terminado'),
        ('cancelled', 'Cancelado'),
        ('with_debt', 'Con Adeudo'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='treatments',
        verbose_name='Paciente'
    )
    
    # Treatment Details
    treatment_type = models.CharField(
        max_length=200,
        verbose_name='Tipo de Tratamiento',
        help_text='Ej: Ortodoncia, Implante, Limpieza, etc.'
    )
    dentist_responsible = models.CharField(
        max_length=200,
        verbose_name='Dentista Responsable'
    )
    
    # Dates
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Finalización'
    )
    
    # Sessions
    total_sessions = models.PositiveIntegerField(
        default=1,
        verbose_name='Número de Sesiones'
    )
    completed_sessions = models.PositiveIntegerField(
        default=0,
        verbose_name='Sesiones Completadas'
    )
    
    # Financial
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Total'
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Cantidad Pagada'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name='Estado'
    )
    
    # Additional Information
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción del Tratamiento'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Tratamiento'
        verbose_name_plural = 'Tratamientos'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"{self.treatment_type} - {self.patient.full_name}"
    
    @property
    def pending_balance(self):
        """Calculate pending balance"""
        return self.total_price - self.amount_paid
    
    @property
    def progress_percentage(self):
        """Calculate treatment progress percentage"""
        if self.total_sessions == 0:
            return 0
        return (self.completed_sessions / self.total_sessions) * 100
    
    @property
    def is_paid(self):
        """Check if treatment is fully paid"""
        return self.amount_paid >= self.total_price


class TreatmentProgress(models.Model):
    """Progress tracking for treatments with photos and notes"""
    
    treatment = models.ForeignKey(
        Treatment,
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name='Tratamiento'
    )
    
    session_number = models.PositiveIntegerField(verbose_name='Número de Sesión')
    date = models.DateField(verbose_name='Fecha')
    comments = models.TextField(verbose_name='Comentarios del Doctor')
    
    # Metadata
    created_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Avance de Tratamiento'
        verbose_name_plural = 'Avances de Tratamiento'
        ordering = ['-date', '-session_number']
        unique_together = ['treatment', 'session_number']
    
    def __str__(self):
        return f"Sesión {self.session_number} - {self.treatment.treatment_type}"


class TreatmentFile(models.Model):
    """Files attached to treatment progress (photos, reports, radiographs)"""
    
    FILE_TYPE_CHOICES = [
        ('photo', 'Foto Clínica'),
        ('radiograph', 'Radiografía'),
        ('report', 'Reporte'),
        ('other', 'Otro'),
    ]
    
    progress = models.ForeignKey(
        TreatmentProgress,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Avance'
    )
    
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        verbose_name='Tipo de Archivo'
    )
    file = models.FileField(
        upload_to='treatment_files/%Y/%m/',
        verbose_name='Archivo'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    
    # Metadata
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')
    
    class Meta:
        verbose_name = 'Archivo de Tratamiento'
        verbose_name_plural = 'Archivos de Tratamiento'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - Sesión {self.progress.session_number}"
