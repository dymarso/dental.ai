from django.db import models
from django.core.exceptions import ValidationError
from patients.models import Patient
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch


class Budget(models.Model):
    """Budget/Quote model for treatment proposals"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('converted', 'Convertido a Tratamiento'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='budgets',
        verbose_name='Paciente'
    )
    
    # Budget Number and Versioning
    budget_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name='Número de Presupuesto',
        help_text='Formato: BUD-YYYYMMDD-XXXX'
    )
    version = models.PositiveIntegerField(
        default=1,
        verbose_name='Versión'
    )
    parent_budget = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revisions',
        verbose_name='Presupuesto Padre',
        help_text='Presupuesto anterior del cual deriva esta versión'
    )
    
    # Budget Details
    title = models.CharField(
        max_length=200,
        verbose_name='Título del Presupuesto'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción General'
    )
    
    # Dates
    created_date = models.DateField(auto_now_add=True, verbose_name='Fecha de Creación')
    valid_until = models.DateField(
        blank=True,
        null=True,
        verbose_name='Válido Hasta'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Total
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Monto Total'
    )
    
    # Notes
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Creado el')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Presupuesto'
        verbose_name_plural = 'Presupuestos'
        ordering = ['-created_date']
    
    def __str__(self):
        return f"{self.title} - {self.patient.full_name}"
    
    def calculate_total(self):
        """Calculate total from all budget items"""
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        return total
    
    def save(self, *args, **kwargs):
        """Override save to generate budget_number if not exists"""
        if not self.budget_number:
            self.budget_number = self._generate_budget_number()
        super().save(*args, **kwargs)
    
    def _generate_budget_number(self):
        """Generate unique budget number in format BUD-YYYYMMDD-XXXX"""
        from django.utils import timezone
        today = timezone.now()
        date_str = today.strftime('%Y%m%d')
        
        # Get the count of budgets created today
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        count = Budget.objects.filter(
            created_at__range=[today_start, today_end]
        ).count()
        
        # Generate sequential number
        sequence = str(count + 1).zfill(4)
        return f"BUD-{date_str}-{sequence}"
    
    def create_new_version(self, user=None):
        """Create a new version of this budget"""
        # Create new budget based on current one
        new_budget = Budget.objects.create(
            patient=self.patient,
            title=self.title,
            description=self.description,
            valid_until=self.valid_until,
            status='pending',
            notes=self.notes,
            created_by=user,
            parent_budget=self,
            version=self.version + 1
        )
        
        # Copy all items
        for item in self.items.all():
            BudgetItem.objects.create(
                budget=new_budget,
                treatment_type=item.treatment_type,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
                order=item.order
            )
        
        # Recalculate total
        new_budget.calculate_total()
        new_budget.save()
        
        return new_budget
    
    def generate_pdf(self):
        """Generate PDF for the budget"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_text = f"Presupuesto {self.budget_number}"
        elements.append(Paragraph(title_text, styles['Title']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Patient and budget info
        info_text = f"""
        <b>Paciente:</b> {self.patient.full_name}<br/>
        <b>Fecha:</b> {self.created_date}<br/>
        <b>Válido hasta:</b> {self.valid_until or 'N/A'}<br/>
        <b>Estado:</b> {self.get_status_display()}<br/>
        <b>Versión:</b> {self.version}
        """
        elements.append(Paragraph(info_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Title
        if self.title:
            elements.append(Paragraph(f"<b>{self.title}</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Items table
        if self.items.exists():
            data = [['Tratamiento', 'Descripción', 'Cant.', 'Precio Unit.', 'Subtotal']]
            
            for item in self.items.all():
                data.append([
                    item.treatment_type,
                    item.description or '-',
                    str(item.quantity),
                    f'${item.unit_price:,.2f}',
                    f'${item.subtotal:,.2f}'
                ])
            
            # Add total row
            data.append(['', '', '', 'TOTAL:', f'${self.total_amount:,.2f}'])
            
            table = Table(data, colWidths=[2*inch, 2*inch, 0.7*inch, 1.2*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                ('GRID', (0, 0), (-1, -2), 1, colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ]))
            
            elements.append(table)
        
        # Notes
        if self.notes:
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("<b>Notas:</b>", styles['Heading3']))
            elements.append(Paragraph(self.notes, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        return pdf


class BudgetItem(models.Model):
    """Individual items in a budget"""
    
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Presupuesto'
    )
    
    # Item Details
    treatment_type = models.CharField(
        max_length=200,
        verbose_name='Tipo de Tratamiento'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    
    # Pricing
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad'
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Unitario'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal'
    )
    
    # Metadata
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden'
    )
    
    class Meta:
        verbose_name = 'Item de Presupuesto'
        verbose_name_plural = 'Items de Presupuesto'
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.treatment_type} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """Calculate subtotal before saving"""
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
