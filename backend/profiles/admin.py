from django.contrib import admin
from .models import DoctorProfile


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialty', 'professional_license', 'clinic_name']
    search_fields = ['full_name', 'professional_license', 'clinic_name']
    ordering = ['full_name']
