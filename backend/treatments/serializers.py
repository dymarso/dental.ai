from rest_framework import serializers
from .models import Treatment, TreatmentProgress, TreatmentFile, OrthodonticCase, AestheticProcedure


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


class OrthodonticCaseSerializer(serializers.ModelSerializer):
    """Serializer for Orthodontic Case model"""
    
    treatment_info = serializers.SerializerMethodField()
    
    class Meta:
        model = OrthodonticCase
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_treatment_info(self, obj):
        """Get basic treatment information"""
        return {
            'id': obj.treatment.id,
            'patient_name': obj.treatment.patient.full_name,
            'treatment_type': obj.treatment.treatment_type
        }


class AestheticProcedureSerializer(serializers.ModelSerializer):
    """Serializer for Aesthetic Procedure model"""
    
    treatment_info = serializers.SerializerMethodField()
    before_photo_url = serializers.SerializerMethodField()
    after_photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = AestheticProcedure
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_treatment_info(self, obj):
        """Get basic treatment information"""
        return {
            'id': obj.treatment.id,
            'patient_name': obj.treatment.patient.full_name,
            'treatment_type': obj.treatment.treatment_type
        }
    
    def get_before_photo_url(self, obj):
        """Get before photo URL"""
        if obj.before_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.before_photo.url)
            return obj.before_photo.url
        return None
    
    def get_after_photo_url(self, obj):
        """Get after photo URL"""
        if obj.after_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.after_photo.url)
            return obj.after_photo.url
        return None
    
    def validate_satisfaction_rating(self, value):
        """Validate satisfaction rating"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError(
                'La calificación de satisfacción debe estar entre 1 y 5'
            )
        return value


class TreatmentSerializer(serializers.ModelSerializer):
    """Serializer for Treatment model"""
    
    pending_balance = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()
    is_paid = serializers.ReadOnlyField()
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    progress_records = TreatmentProgressSerializer(many=True, read_only=True)
    orthodontic_case = OrthodonticCaseSerializer(read_only=True)
    aesthetic_procedure = AestheticProcedureSerializer(read_only=True)
    
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
            'orthodontic_case',
            'aesthetic_procedure',
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

