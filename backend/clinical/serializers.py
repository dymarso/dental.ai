from rest_framework import serializers
from .models import MedicalHistory, ClinicalNote, ClinicalFile, Odontogram, Periodontogram


class MedicalHistorySerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = MedicalHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClinicalNoteSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = ClinicalNote
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClinicalFileSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ClinicalFile
        fields = '__all__'
        read_only_fields = ['id', 'uploaded_at']
    
    def get_file_url(self, obj):
        """Get the file URL"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class OdontogramSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = Odontogram
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_tooth_data(self, value):
        """Validate tooth_data structure"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('tooth_data debe ser un diccionario')
        
        # Validate tooth numbers
        valid_permanent = set(range(11, 19)) | set(range(21, 29)) | set(range(31, 39)) | set(range(41, 49))
        valid_deciduous = set(range(51, 56)) | set(range(61, 66)) | set(range(71, 76)) | set(range(81, 86))
        valid_teeth = valid_permanent | valid_deciduous
        
        for tooth_num in value.keys():
            try:
                tooth_int = int(tooth_num)
                if tooth_int not in valid_teeth:
                    raise serializers.ValidationError(
                        f'Número de diente inválido: {tooth_num}'
                    )
            except (ValueError, TypeError):
                raise serializers.ValidationError(
                    f'Número de diente debe ser entero: {tooth_num}'
                )
        
        return value


class PeriodontogramSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    
    class Meta:
        model = Periodontogram
        fields = '__all__'
        read_only_fields = ['id', 'has_abnormal_values', 'created_at', 'updated_at']
    
    def validate_measurements(self, value):
        """Validate measurements structure and values"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('measurements debe ser un diccionario')
        
        # Validate each tooth's measurements
        for tooth_num, tooth_measurements in value.items():
            # Each tooth should have exactly 6 measurements
            if not isinstance(tooth_measurements, (list, tuple)):
                raise serializers.ValidationError(
                    f'Mediciones para diente {tooth_num} deben ser una lista'
                )
            
            if len(tooth_measurements) != 6:
                raise serializers.ValidationError(
                    f'Diente {tooth_num} debe tener exactamente 6 mediciones'
                )
            
            # Validate each measurement (0-15mm)
            for i, measurement in enumerate(tooth_measurements):
                try:
                    value_float = float(measurement)
                    if value_float < 0 or value_float > 15:
                        raise serializers.ValidationError(
                            f'Medición {i+1} del diente {tooth_num} fuera de rango (0-15mm): {value_float}'
                        )
                except (ValueError, TypeError):
                    raise serializers.ValidationError(
                        f'Medición {i+1} del diente {tooth_num} debe ser numérica'
                    )
        
        return value
