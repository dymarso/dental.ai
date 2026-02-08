from django.contrib import admin
from .models import Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'start_date', 'end_date', 'export_format', 'generated_at']
    list_filter = ['report_type', 'export_format', 'generated_at']
    search_fields = ['title', 'description']
    ordering = ['-generated_at']
