from rest_framework import serializers
from .models import Agreement


class AgreementSerializer(serializers.ModelSerializer):
    """Serializer for Agreement model"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True, allow_null=True)
    agreement_type_display = serializers.CharField(source='get_agreement_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_signed = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Agreement
        fields = [
            'id',
            'patient',
            'patient_name',
            'created_by',
            'created_by_name',
            'agreement_type',
            'agreement_type_display',
            'title',
            'content',
            'status',
            'status_display',
            'signature_data',
            'signed_by_name',
            'signed_at',
            'ip_address',
            'expires_at',
            'pdf_file',
            'notes',
            'is_signed',
            'is_expired',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'signed_at', 'ip_address', 'created_at', 'updated_at']


class AgreementListSerializer(serializers.ModelSerializer):
    """Simplified serializer for agreement list view"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    agreement_type_display = serializers.CharField(source='get_agreement_type_display', read_only=True)
    is_signed = serializers.ReadOnlyField()
    
    class Meta:
        model = Agreement
        fields = [
            'id',
            'patient_name',
            'agreement_type_display',
            'title',
            'status',
            'is_signed',
            'signed_at',
            'created_at',
        ]


class SignAgreementSerializer(serializers.Serializer):
    """Serializer for signing an agreement"""
    
    signature_data = serializers.CharField(required=True)
    signed_by_name = serializers.CharField(required=True, max_length=200)
