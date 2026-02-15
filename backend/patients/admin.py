from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['patient_number', 'full_name', 'phone', 'email', 'age', 'gender', 'is_active', 'is_deleted', 'created_at']
    list_filter = ['gender', 'is_active', 'is_deleted', 'preferred_contact_method', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'patient_number', 'uuid']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['uuid', 'patient_number', 'created_at', 'updated_at', 'deleted_at']
    
    fieldsets = (
        ('Identificación', {
            'fields': ('uuid', 'patient_number')
        }),
        ('Información Básica', {
            'fields': ('first_name', 'last_name', 'gender', 'date_of_birth')
        }),
        ('Información de Contacto', {
            'fields': ('phone', 'email', 'preferred_contact_method')
        }),
        ('Contacto de Emergencia', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Estado', {
            'fields': ('is_active', 'is_deleted', 'deleted_at')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['soft_delete_patients', 'restore_patients']
    
    def soft_delete_patients(self, request, queryset):
        """Soft delete selected patients"""
        count = 0
        for patient in queryset:
            if not patient.is_deleted:
                patient.soft_delete()
                count += 1
        self.message_user(request, f'{count} paciente(s) eliminado(s) exitosamente.')
    soft_delete_patients.short_description = 'Eliminar pacientes seleccionados (soft delete)'
    
    def restore_patients(self, request, queryset):
        """Restore soft-deleted patients"""
        count = 0
        for patient in queryset:
            if patient.is_deleted:
                patient.restore()
                count += 1
        self.message_user(request, f'{count} paciente(s) restaurado(s) exitosamente.')
    restore_patients.short_description = 'Restaurar pacientes eliminados'
