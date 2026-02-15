from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    method_display = serializers.CharField(source='get_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'patient',
            'patient_name',
            'appointment',
            'notification_type',
            'notification_type_display',
            'method',
            'method_display',
            'subject',
            'message',
            'recipient_email',
            'recipient_phone',
            'status',
            'status_display',
            'scheduled_for',
            'sent_at',
            'response_data',
            'error_message',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'sent_at', 'response_data', 'error_message', 'created_at', 'updated_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    
    class Meta:
        model = Notification
        fields = [
            'patient',
            'appointment',
            'notification_type',
            'method',
            'subject',
            'message',
            'recipient_email',
            'recipient_phone',
            'scheduled_for',
        ]
    
    def validate(self, attrs):
        """Validate recipient information based on method"""
        method = attrs.get('method')
        patient = attrs.get('patient')
        
        if method == 'email':
            if not attrs.get('recipient_email') and not patient.email:
                raise serializers.ValidationError('Se requiere un email para enviar notificaciones por correo')
            attrs['recipient_email'] = attrs.get('recipient_email') or patient.email
        
        elif method in ['sms', 'whatsapp']:
            if not attrs.get('recipient_phone') and not patient.phone:
                raise serializers.ValidationError('Se requiere un teléfono para enviar notificaciones por SMS/WhatsApp')
            attrs['recipient_phone'] = attrs.get('recipient_phone') or patient.phone
        
        return attrs


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer for sending bulk notifications"""
    
    patients = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    notification_type = serializers.ChoiceField(
        choices=Notification.TYPE_CHOICES,
        required=True
    )
    method = serializers.ChoiceField(
        choices=Notification.METHOD_CHOICES,
        required=True
    )
    subject = serializers.CharField(max_length=200, required=False, allow_blank=True)
    message = serializers.CharField(required=True)
    scheduled_for = serializers.DateTimeField(required=False, allow_null=True)
