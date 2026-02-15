from django.db import models
from django.core.exceptions import ValidationError
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


class OrthodonticCase(models.Model):
    """Orthodontic case tracking for treatments"""
    
    APPLIANCE_TYPE_CHOICES = [
        ('metal_braces', 'Brackets Metálicos'),
        ('ceramic_braces', 'Brackets Cerámicos'),
        ('lingual_braces', 'Brackets Linguales'),
        ('invisalign', 'Invisalign'),
        ('clear_aligners', 'Alineadores Transparentes'),
        ('retainer', 'Retenedor'),
        ('other', 'Otro'),
    ]
    
    treatment = models.OneToOneField(
        Treatment,
        on_delete=models.CASCADE,
        related_name='orthodontic_case',
        verbose_name='Tratamiento'
    )
    
    appliance_type = models.CharField(
        max_length=50,
        choices=APPLIANCE_TYPE_CHOICES,
        verbose_name='Tipo de Aparato'
    )
    
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    expected_end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha Estimada de Finalización'
    )
    
    adjustments = models.JSONField(
        default=list,
        verbose_name='Historial de Ajustes',
        help_text='Array de objetos con historial de ajustes'
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
        verbose_name = 'Caso de Ortodoncia'
        verbose_name_plural = 'Casos de Ortodoncia'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Ortodoncia - {self.treatment.patient.full_name} ({self.appliance_type})"
    
    def add_adjustment(self, date, description, performed_by=None):
        """Add an adjustment to the history"""
        adjustment = {
            'date': date.isoformat() if hasattr(date, 'isoformat') else date,
            'description': description,
            'performed_by': performed_by
        }
        
        if not isinstance(self.adjustments, list):
            self.adjustments = []
        
        self.adjustments.append(adjustment)
        self.save()


class AestheticProcedure(models.Model):
    """Aesthetic procedure tracking for treatments"""
    
    PROCEDURE_TYPE_CHOICES = [
        ('whitening', 'Blanqueamiento'),
        ('veneers', 'Carillas'),
        ('bonding', 'Bonding'),
        ('gum_contouring', 'Contorneado de Encías'),
        ('smile_design', 'Diseño de Sonrisa'),
        ('composite_filling', 'Resina Estética'),
        ('other', 'Otro'),
    ]
    
    treatment = models.OneToOneField(
        Treatment,
        on_delete=models.CASCADE,
        related_name='aesthetic_procedure',
        verbose_name='Tratamiento'
    )
    
    procedure_type = models.CharField(
        max_length=50,
        choices=PROCEDURE_TYPE_CHOICES,
        verbose_name='Tipo de Procedimiento'
    )
    
    product_used = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Producto Utilizado',
        help_text='Marca/nombre del producto utilizado'
    )
    
    before_photo = models.ImageField(
        upload_to='aesthetic_procedures/before/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Foto Antes'
    )
    
    after_photo = models.ImageField(
        upload_to='aesthetic_procedures/after/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Foto Después'
    )
    
    satisfaction_rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Calificación de Satisfacción',
        help_text='1-5 estrellas'
    )
    
    completion_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Finalización'
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
        verbose_name = 'Procedimiento Estético'
        verbose_name_plural = 'Procedimientos Estéticos'
        ordering = ['-completion_date', '-created_at']
    
    def __str__(self):
        return f"{self.get_procedure_type_display()} - {self.treatment.patient.full_name}"
    
    def clean(self):
        """Validate satisfaction rating"""
        super().clean()
        
        if self.satisfaction_rating is not None:
            if self.satisfaction_rating < 1 or self.satisfaction_rating > 5:
                raise ValidationError(
                    'La calificación de satisfacción debe estar entre 1 y 5'
                )


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
