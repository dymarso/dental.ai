from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for Patient model"""
    
    age = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    whatsapp_link = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'uuid',
            'patient_number',
            'first_name',
            'last_name',
            'full_name',
            'gender',
            'date_of_birth',
            'age',
            'phone',
            'email',
            'preferred_contact_method',
            'whatsapp_link',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relationship',
            'notes',
            'is_active',
            'is_deleted',
            'deleted_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'uuid', 'patient_number', 'created_at', 'updated_at', 'deleted_at']


class PatientListSerializer(serializers.ModelSerializer):
    """Simplified serializer for patient list view"""
    
    age = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Patient
        fields = [
            'id',
            'full_name',
            'gender',
            'age',
            'phone',
            'email',
            'is_active',
        ]
