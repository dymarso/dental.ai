from django.contrib import admin
from .models import Treatment, TreatmentProgress, TreatmentFile


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ['treatment_type', 'patient', 'dentist_responsible', 'start_date', 'status', 'total_price', 'pending_balance']
    list_filter = ['status', 'start_date', 'dentist_responsible']
    search_fields = ['treatment_type', 'patient__first_name', 'patient__last_name']
    ordering = ['-start_date']


@admin.register(TreatmentProgress)
class TreatmentProgressAdmin(admin.ModelAdmin):
    list_display = ['treatment', 'session_number', 'date', 'created_by']
    list_filter = ['date', 'created_by']
    ordering = ['-date']


@admin.register(TreatmentFile)
class TreatmentFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'progress', 'file_type', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    ordering = ['-uploaded_at']
