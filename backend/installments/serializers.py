from rest_framework import serializers
from .models import InstallmentPlan, InstallmentPayment


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    """Serializer for InstallmentPayment model"""
    
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = InstallmentPayment
        fields = [
            'id',
            'installment_plan',
            'installment_number',
            'amount',
            'due_date',
            'payment_date',
            'status',
            'payment_method',
            'notes',
            'is_overdue',
            'days_overdue',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstallmentPlanSerializer(serializers.ModelSerializer):
    """Serializer for InstallmentPlan model"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    paid_amount = serializers.ReadOnlyField()
    pending_amount = serializers.ReadOnlyField()
    paid_installments = serializers.ReadOnlyField()
    pending_installments = serializers.ReadOnlyField()
    is_delinquent = serializers.ReadOnlyField()
    payments = InstallmentPaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = InstallmentPlan
        fields = [
            'id',
            'patient',
            'patient_name',
            'budget',
            'total_amount',
            'number_of_installments',
            'installment_amount',
            'status',
            'start_date',
            'notes',
            'paid_amount',
            'pending_amount',
            'paid_installments',
            'pending_installments',
            'is_delinquent',
            'payments',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InstallmentPlanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating installment plans with automatic payment generation"""
    
    class Meta:
        model = InstallmentPlan
        fields = [
            'patient',
            'budget',
            'total_amount',
            'number_of_installments',
            'installment_amount',
            'start_date',
            'notes',
        ]
    
    def create(self, validated_data):
        """Create installment plan and generate payment schedule"""
        from dateutil.relativedelta import relativedelta
        
        plan = InstallmentPlan.objects.create(**validated_data)
        
        # Generate installment payments
        for i in range(plan.number_of_installments):
            due_date = plan.start_date + relativedelta(months=i)
            
            InstallmentPayment.objects.create(
                installment_plan=plan,
                installment_number=i + 1,
                amount=plan.installment_amount,
                due_date=due_date,
                status='pending'
            )
        
        return plan
