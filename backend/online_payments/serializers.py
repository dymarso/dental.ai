from rest_framework import serializers
from .models import OnlinePayment, StripePayment


class StripePaymentSerializer(serializers.ModelSerializer):
    """Serializer for StripePayment model"""
    
    class Meta:
        model = StripePayment
        fields = [
            'id',
            'stripe_payment_intent_id',
            'stripe_customer_id',
            'stripe_charge_id',
            'card_brand',
            'card_last4',
            'card_exp_month',
            'card_exp_year',
            'stripe_metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class OnlinePaymentSerializer(serializers.ModelSerializer):
    """Serializer for OnlinePayment model"""
    
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    stripe_details = StripePaymentSerializer(read_only=True)
    
    class Meta:
        model = OnlinePayment
        fields = [
            'id',
            'patient',
            'patient_name',
            'installment_payment',
            'amount',
            'currency',
            'payment_method',
            'payment_method_display',
            'status',
            'status_display',
            'transaction_id',
            'gateway_response',
            'payment_date',
            'completed_at',
            'customer_email',
            'customer_name',
            'notes',
            'error_message',
            'stripe_details',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'transaction_id', 'gateway_response', 'payment_date', 
                            'completed_at', 'error_message', 'created_at', 'updated_at']


class CreatePaymentIntentSerializer(serializers.Serializer):
    """Serializer for creating a Stripe payment intent"""
    
    patient_id = serializers.IntegerField(required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    currency = serializers.CharField(max_length=3, default='mxn')
    installment_payment_id = serializers.IntegerField(required=False, allow_null=True)
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)


class ConfirmPaymentSerializer(serializers.Serializer):
    """Serializer for confirming a payment"""
    
    payment_intent_id = serializers.CharField(required=True)
