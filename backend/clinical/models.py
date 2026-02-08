from django.db import models
from patients.models import Patient


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
        verbose_name='Archivo'
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
