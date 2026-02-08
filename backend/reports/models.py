from django.db import models
from django.utils import timezone


class Report(models.Model):
    """Report generation and storage model"""
    
    REPORT_TYPE_CHOICES = [
        ('daily_income', 'Ingresos Diarios'),
        ('weekly_income', 'Ingresos Semanales'),
        ('monthly_income', 'Ingresos Mensuales'),
        ('daily_expenses', 'Gastos Diarios'),
        ('weekly_expenses', 'Gastos Semanales'),
        ('monthly_expenses', 'Gastos Mensuales'),
        ('common_treatments', 'Tratamientos Más Comunes'),
        ('patients_with_debt', 'Pacientes con Adeudo'),
        ('custom', 'Personalizado'),
    ]
    
    EXPORT_FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]
    
    # Report Details
    report_type = models.CharField(
        max_length=50,
        choices=REPORT_TYPE_CHOICES,
        verbose_name='Tipo de Reporte'
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
    
    # Date Range
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    end_date = models.DateField(verbose_name='Fecha de Fin')
    
    # Export
    export_format = models.CharField(
        max_length=10,
        choices=EXPORT_FORMAT_CHOICES,
        verbose_name='Formato de Exportación'
    )
    file = models.FileField(
        upload_to='reports/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Archivo Generado'
    )
    
    # Results (JSON data)
    data = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Datos del Reporte'
    )
    
    # Metadata
    generated_by = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Generado por'
    )
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Generación')
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"{self.title} ({self.start_date} - {self.end_date})"
