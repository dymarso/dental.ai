from rest_framework import serializers
from .models import Budget, BudgetItem


class BudgetItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetItem
        fields = '__all__'
        read_only_fields = ['id', 'subtotal']


class BudgetSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    items = BudgetItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_date']
