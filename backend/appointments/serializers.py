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
            'telemedicine_enabled',
            'video_link',
            'public_booking',
            'created_by',
            'notes',
            'reminder_sent',
            'reminder_sent_at',
            'reminders',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Custom validation"""
        # Create a temporary appointment object for validation
        instance = self.instance or Appointment()
        for key, value in data.items():
            setattr(instance, key, value)
        
        # Check business hours
        if not instance.is_within_business_hours():
            raise serializers.ValidationError(
                'Las citas deben ser entre las 8:00 AM y las 8:00 PM'
            )
        
        # Check conflicts (only if not updating or if date/time changed)
        if instance.has_conflicts():
            raise serializers.ValidationError(
                'Ya existe una cita en este horario para esta unidad dental'
            )
        
        return data
