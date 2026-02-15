from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from patients.models import Patient
import os
import uuid


class MedicalHistory(models.Model):
    """Medical history record for a patient"""
    
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_history',
        verbose_name='Paciente'
    )
    
    # Medical Conditions
    chronic_diseases = models.TextField(
        blank=True,
        null=True,
        verbose_name='Enfermedades Crónicas',
        help_text='Diabetes, hipertensión, etc.'
    )
    current_medications = models.TextField(
        blank=True,
        null=True,
        verbose_name='Medicamentos Actuales'
    )
    allergies = models.TextField(
        blank=True,
        null=True,
        verbose_name='Alergias',
        help_text='Medicamentos, materiales dentales, etc.'
    )
    previous_dental_treatments = models.TextField(
        blank=True,
        null=True,
        verbose_name='Tratamientos Dentales Previos'
    )
    
    # Habits
    smoking = models.BooleanField(
        default=False,
        verbose_name='Fumador'
    )
    alcohol_consumption = models.BooleanField(
        default=False,
        verbose_name='Consume Alcohol'
    )
    
    # Other observations
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas Adicionales'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Historial Médico'
        verbose_name_plural = 'Historiales Médicos'
    
    def __str__(self):
        return f"Historial médico de {self.patient.full_name}"


class ClinicalNote(models.Model):
    """Clinical notes and observations for a patient"""
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='clinical_notes',
        verbose_name='Paciente'
    )
    
    date = models.DateField(verbose_name='Fecha')
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción')
    observations = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones Clínicas'
    )
    
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
        verbose_name = 'Nota Clínica'
        verbose_name_plural = 'Notas Clínicas'
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.patient.full_name} ({self.date})"


class ClinicalFile(models.Model):
    """Files attached to patient clinical records (photos, PDFs, radiographs)"""
    
    FILE_TYPE_CHOICES = [
        ('photo', 'Foto Clínica'),
        ('radiograph', 'Radiografía'),
        ('pdf', 'Documento PDF'),
        ('other', 'Otro'),
    ]
    
    # Max file size in bytes (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'heic', 'pdf', 'docx']
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='clinical_files',
        verbose_name='Paciente'
    )
    
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        verbose_name='Tipo de Archivo'
    )
    file = models.FileField(
        upload_to='clinical_files/%Y/%m/',
        verbose_name='Archivo',
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)]
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    date_taken = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de Toma'
    )
    
    # Link to clinical note (optional)
    clinical_note = models.ForeignKey(
        ClinicalNote,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files',
        verbose_name='Nota Clínica'
    )
    
    # Metadata
    uploaded_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Subido por'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')
    
    class Meta:
        verbose_name = 'Archivo Clínico'
        verbose_name_plural = 'Archivos Clínicos'
        ordering = ['-date_taken', '-uploaded_at']
    
    def __str__(self):
        return f"{self.title} - {self.patient.full_name}"
    
    def clean(self):
        """Validate file size and type"""
        super().clean()
        
        if self.file:
            # Validate file size
            if self.file.size > self.MAX_FILE_SIZE:
                raise ValidationError(
                    f'El archivo no puede superar los {self.MAX_FILE_SIZE / (1024*1024)}MB'
                )
            
            # Validate file extension
            ext = os.path.splitext(self.file.name)[1][1:].lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                raise ValidationError(
                    f'Tipo de archivo no permitido. Extensiones permitidas: {", ".join(self.ALLOWED_EXTENSIONS)}'
                )
    
    def save(self, *args, **kwargs):
        """Generate unique filename and validate before saving"""
        if self.file and not self.pk:
            # Generate unique filename
            ext = os.path.splitext(self.file.name)[1]
            unique_filename = f"{uuid.uuid4()}{ext}"
            self.file.name = unique_filename
        
        self.full_clean()
        super().save(*args, **kwargs)


class Odontogram(models.Model):
    """Dental chart for tracking tooth conditions"""
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='odontograms',
        verbose_name='Paciente'
    )
    
    tooth_data = models.JSONField(
        default=dict,
        verbose_name='Datos de Dientes',
        help_text='JSON con información de cada diente (20 o 32 dientes)'
    )
    
    date = models.DateField(verbose_name='Fecha')
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
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
        verbose_name = 'Odontograma'
        verbose_name_plural = 'Odontogramas'
        ordering = ['-date']
        unique_together = ['patient', 'date']
    
    def __str__(self):
        return f"Odontograma - {self.patient.full_name} ({self.date})"
    
    def clean(self):
        """Validate tooth_data structure"""
        super().clean()
        
        if self.tooth_data:
            # Validate that tooth_data is a dict
            if not isinstance(self.tooth_data, dict):
                raise ValidationError('tooth_data debe ser un diccionario')
            
            # Validate tooth numbers (1-32 for permanent, 51-85 for deciduous)
            valid_permanent = set(range(11, 19)) | set(range(21, 29)) | set(range(31, 39)) | set(range(41, 49))
            valid_deciduous = set(range(51, 56)) | set(range(61, 66)) | set(range(71, 76)) | set(range(81, 86))
            valid_teeth = valid_permanent | valid_deciduous
            
            for tooth_num in self.tooth_data.keys():
                try:
                    tooth_int = int(tooth_num)
                    if tooth_int not in valid_teeth:
                        raise ValidationError(
                            f'Número de diente inválido: {tooth_num}'
                        )
                except (ValueError, TypeError):
                    raise ValidationError(
                        f'Número de diente debe ser entero: {tooth_num}'
                    )


class Periodontogram(models.Model):
    """Periodontal chart for gum measurements"""
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='periodontograms',
        verbose_name='Paciente'
    )
    
    measurements = models.JSONField(
        default=dict,
        verbose_name='Mediciones',
        help_text='JSON con 6 mediciones por diente (rango 0-15mm)'
    )
    
    date = models.DateField(verbose_name='Fecha')
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Notas'
    )
    
    has_abnormal_values = models.BooleanField(
        default=False,
        verbose_name='Tiene Valores Anormales',
        help_text='Se marca automáticamente si hay valores >3mm'
    )
    
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
        verbose_name = 'Periodontograma'
        verbose_name_plural = 'Periodontogramas'
        ordering = ['-date']
        unique_together = ['patient', 'date']
    
    def __str__(self):
        return f"Periodontograma - {self.patient.full_name} ({self.date})"
    
    def clean(self):
        """Validate measurements structure and values"""
        super().clean()
        
        if self.measurements:
            # Validate that measurements is a dict
            if not isinstance(self.measurements, dict):
                raise ValidationError('measurements debe ser un diccionario')
            
            # Validate each tooth's measurements
            for tooth_num, tooth_measurements in self.measurements.items():
                # Each tooth should have exactly 6 measurements
                if not isinstance(tooth_measurements, (list, tuple)):
                    raise ValidationError(
                        f'Mediciones para diente {tooth_num} deben ser una lista'
                    )
                
                if len(tooth_measurements) != 6:
                    raise ValidationError(
                        f'Diente {tooth_num} debe tener exactamente 6 mediciones'
                    )
                
                # Validate each measurement (0-15mm)
                for i, measurement in enumerate(tooth_measurements):
                    try:
                        value = float(measurement)
                        if value < 0 or value > 15:
                            raise ValidationError(
                                f'Medición {i+1} del diente {tooth_num} fuera de rango (0-15mm): {value}'
                            )
                    except (ValueError, TypeError):
                        raise ValidationError(
                            f'Medición {i+1} del diente {tooth_num} debe ser numérica'
                        )
    
    def save(self, *args, **kwargs):
        """Check for abnormal values before saving"""
        self.full_clean()
        
        # Check for abnormal values (>3mm)
        self.has_abnormal_values = False
        if self.measurements:
            for tooth_measurements in self.measurements.values():
                if any(float(m) > 3 for m in tooth_measurements):
                    self.has_abnormal_values = True
                    break
        
        super().save(*args, **kwargs)
