from django.contrib import admin
from .models import MedicalHistory, ClinicalNote, ClinicalFile


@admin.register(MedicalHistory)
class MedicalHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient', 'smoking', 'alcohol_consumption', 'updated_at']
    list_filter = ['smoking', 'alcohol_consumption']
    search_fields = ['patient__first_name', 'patient__last_name']
    ordering = ['-updated_at']


@admin.register(ClinicalNote)
class ClinicalNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'date', 'created_by']
    list_filter = ['date', 'created_by']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    ordering = ['-date']


@admin.register(ClinicalFile)
class ClinicalFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'file_type', 'date_taken', 'uploaded_at']
    list_filter = ['file_type', 'date_taken', 'uploaded_at']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    ordering = ['-uploaded_at']
