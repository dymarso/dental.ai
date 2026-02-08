from rest_framework import serializers
from .models import Appointment, AppointmentReminder


class AppointmentReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentReminder
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    reminders = AppointmentReminderSerializer(many=True, read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient',
            'patient_name',
            'consultation_type',
            'date',
            'start_time',
            'end_time',
            'duration_minutes',
            'dental_unit',
            'status',
            'notes',
            'reminder_sent',
            'reminder_sent_at',
            'reminders',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
