from django.contrib import admin
from .models import MedicalHistory, ClinicalNote, ClinicalFile, Odontogram, Periodontogram


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'smoking', 'alcohol_consumption', 'updated_at']
    list_filter = ['smoking', 'alcohol_consumption']
    search_fields = ['patient__first_name', 'patient__last_name']
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ClinicalNote)
class ClinicalNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'date', 'created_by']
    list_filter = ['date', 'created_by']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    ordering = ['-date']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ClinicalFile)
class ClinicalFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'file_type', 'date_taken', 'uploaded_at']
    list_filter = ['file_type', 'date_taken', 'uploaded_at']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    ordering = ['-uploaded_at']
    date_hierarchy = 'uploaded_at'
    readonly_fields = ['uploaded_at']


@admin.register(Odontogram)
class OdontogramAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date', 'created_by', 'created_at']
    list_filter = ['date', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name']
    ordering = ['-date']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Periodontogram)
class PeriodontogramAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date', 'has_abnormal_values', 'created_by', 'created_at']
    list_filter = ['date', 'has_abnormal_values', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name']
    ordering = ['-date']
    date_hierarchy = 'date'
    readonly_fields = ['has_abnormal_values', 'created_at', 'updated_at']

