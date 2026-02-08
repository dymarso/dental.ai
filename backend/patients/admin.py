from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'email', 'age', 'gender', 'is_active', 'created_at']
    list_filter = ['gender', 'is_active', 'preferred_contact_method', 'created_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('first_name', 'last_name', 'gender', 'date_of_birth')
        }),
        ('Información de Contacto', {
            'fields': ('phone', 'email', 'preferred_contact_method')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )
