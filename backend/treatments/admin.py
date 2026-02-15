from django.contrib import admin
from .models import Treatment, TreatmentProgress, TreatmentFile, OrthodonticCase, AestheticProcedure


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    list_display = ['treatment_type', 'patient', 'dentist_responsible', 'start_date', 'status', 'total_price', 'pending_balance']
    list_filter = ['status', 'start_date', 'dentist_responsible']
    search_fields = ['treatment_type', 'patient__first_name', 'patient__last_name']
    ordering = ['-start_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TreatmentProgress)
class TreatmentProgressAdmin(admin.ModelAdmin):
    list_display = ['treatment', 'session_number', 'date', 'created_by']
    list_filter = ['date', 'created_by']
    ordering = ['-date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TreatmentFile)
class TreatmentFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'progress', 'file_type', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    ordering = ['-uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(OrthodonticCase)
class OrthodonticCaseAdmin(admin.ModelAdmin):
    list_display = ['treatment', 'appliance_type', 'start_date', 'expected_end_date']
    list_filter = ['appliance_type', 'start_date']
    search_fields = ['treatment__patient__first_name', 'treatment__patient__last_name']
    ordering = ['-start_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AestheticProcedure)
class AestheticProcedureAdmin(admin.ModelAdmin):
    list_display = ['treatment', 'procedure_type', 'satisfaction_rating', 'completion_date']
    list_filter = ['procedure_type', 'satisfaction_rating', 'completion_date']
    search_fields = ['treatment__patient__first_name', 'treatment__patient__last_name', 'product_used']
    ordering = ['-completion_date']
    readonly_fields = ['created_at', 'updated_at']

