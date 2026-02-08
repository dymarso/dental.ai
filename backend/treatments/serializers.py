from rest_framework import serializers
from .models import Treatment, TreatmentProgress, TreatmentFile


class TreatmentFileSerializer(serializers.ModelSerializer):
    """Serializer for Treatment File model"""
    
    class Meta:
        model = TreatmentFile
        fields = [
            'id',
            'progress',
            'file_type',
            'file',
            'title',
            'description',
            'uploaded_at',
        ]
        read_only_fields = ['id', 'uploaded_at']


class TreatmentProgressSerializer(serializers.ModelSerializer):
    """Serializer for Treatment Progress model"""
    
    files = TreatmentFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = TreatmentProgress
        fields = [
            'id',
            'treatment',
            'session_number',
            'date',
            'comments',
            'files',
            'created_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TreatmentSerializer(serializers.ModelSerializer):
    """Serializer for Treatment model"""
    
    pending_balance = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    is_paid = serializers.ReadOnlyField()
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    progress_records = TreatmentProgressSerializer(many=True, read_only=True)
    
    class Meta:
        model = Treatment
        fields = [
            'id',
            'patient',
            'patient_name',
            'treatment_type',
            'dentist_responsible',
            'start_date',
            'end_date',
            'total_sessions',
            'completed_sessions',
            'total_price',
            'amount_paid',
            'pending_balance',
            'progress_percentage',
            'is_paid',
            'status',
            'description',
            'notes',
            'progress_records',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TreatmentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for treatment list view"""
    
    pending_balance = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = Treatment
        fields = [
            'id',
            'patient',
            'patient_name',
            'treatment_type',
            'start_date',
            'status',
            'total_price',
            'amount_paid',
            'pending_balance',
            'progress_percentage',
        ]
