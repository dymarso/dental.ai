from django.contrib import admin
from .models import Agreement


@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'agreement_type', 'status', 'signed_at', 'is_signed']
    list_filter = ['agreement_type', 'status', 'created_at', 'signed_at']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['signature_data', 'signed_at', 'ip_address', 'pdf_file', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Paciente', {
            'fields': ('patient', 'created_by')
        }),
        ('Detalles del Acuerdo', {
            'fields': ('agreement_type', 'title', 'content', 'status')
        }),
        ('Firma', {
            'fields': ('signature_data', 'signed_by_name', 'signed_at', 'ip_address')
        }),
        ('Fechas', {
            'fields': ('expires_at', 'created_at', 'updated_at')
        }),
        ('Archivo', {
            'fields': ('pdf_file',)
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
    )
    
    def is_signed(self, obj):
        return obj.is_signed
    is_signed.boolean = True
    is_signed.short_description = 'Firmado'
