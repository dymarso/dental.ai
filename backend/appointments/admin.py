from django.contrib import admin
from .models import Appointment, AppointmentReminder


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date', 'start_time', 'end_time', 'consultation_type', 'status']
    list_filter = ['status', 'consultation_type', 'date']
    search_fields = ['patient__first_name', 'patient__last_name']
    ordering = ['date', 'start_time']


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    list_display = ['appointment', 'method', 'sent_at', 'success']
    list_filter = ['method', 'success', 'sent_at']
    ordering = ['-sent_at']
