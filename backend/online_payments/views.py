from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import os
import uuid

from .models import OnlinePayment, StripePayment
from .serializers import (
    OnlinePaymentSerializer,
    StripePaymentSerializer,
    CreatePaymentIntentSerializer,
    ConfirmPaymentSerializer
)


class OnlinePaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing online payments
    """
    queryset = OnlinePayment.objects.select_related('patient', 'installment_payment')
    serializer_class = OnlinePaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'payment_method', 'status', 'installment_payment']
    search_fields = ['patient__first_name', 'patient__last_name', 'transaction_id']
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def create_payment_intent(self, request):
        """Create a Stripe payment intent"""
        serializer = CreatePaymentIntentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get Stripe API key
        stripe_api_key = os.getenv('STRIPE_SECRET_KEY')
        if not stripe_api_key:
            return Response(
                {'error': 'Stripe not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        try:
            import stripe
            stripe.api_key = stripe_api_key
            
            from patients.models import Patient
            patient = Patient.objects.get(id=serializer.validated_data['patient_id'])
            
            # Create payment intent
            payment_intent = stripe.PaymentIntent.create(
                amount=int(serializer.validated_data['amount'] * 100),  # Convert to cents
                currency=serializer.validated_data.get('currency', 'mxn'),
                description=serializer.validated_data.get('description', f'Pago de {patient.full_name}'),
                metadata={
                    'patient_id': patient.id,
                    'patient_name': patient.full_name,
                    'installment_payment_id': serializer.validated_data.get('installment_payment_id', '')
                }
            )
            
            # Create OnlinePayment record
            transaction_id = f"stripe_{payment_intent.id}"
            online_payment = OnlinePayment.objects.create(
                patient=patient,
                installment_payment_id=serializer.validated_data.get('installment_payment_id'),
                amount=serializer.validated_data['amount'],
                currency=serializer.validated_data.get('currency', 'MXN').upper(),
                payment_method='stripe',
                status='pending',
                transaction_id=transaction_id,
                customer_email=patient.email,
                customer_name=patient.full_name,
                gateway_response={'payment_intent_id': payment_intent.id}
            )
            
            # Create StripePayment record
            stripe_payment = StripePayment.objects.create(
                online_payment=online_payment,
                stripe_payment_intent_id=payment_intent.id
            )
            
            return Response({
                'payment_id': online_payment.id,
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def confirm_payment(self, request):
        """Confirm a payment after client-side confirmation"""
        serializer = ConfirmPaymentSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payment_intent_id = serializer.validated_data['payment_intent_id']
        
        try:
            # Get payment record
            stripe_payment = StripePayment.objects.get(stripe_payment_intent_id=payment_intent_id)
            online_payment = stripe_payment.online_payment
            
            # Retrieve payment intent from Stripe
            import stripe
            stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
            
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Update payment status
            if payment_intent.status == 'succeeded':
                online_payment.status = 'completed'
                online_payment.completed_at = timezone.now()
                
                # Update card information
                if payment_intent.charges.data:
                    charge = payment_intent.charges.data[0]
                    stripe_payment.stripe_charge_id = charge.id
                    
                    if charge.payment_method_details.card:
                        card = charge.payment_method_details.card
                        stripe_payment.card_brand = card.brand
                        stripe_payment.card_last4 = card.last4
                        stripe_payment.card_exp_month = card.exp_month
                        stripe_payment.card_exp_year = card.exp_year
                
                # Mark installment payment as paid if linked
                if online_payment.installment_payment:
                    installment = online_payment.installment_payment
                    installment.status = 'paid'
                    installment.payment_method = 'card'
                    installment.payment_date = timezone.now().date()
                    installment.notes = f'Paid via Stripe: {payment_intent_id}'
                    installment.save()
                
            elif payment_intent.status == 'requires_payment_method':
                online_payment.status = 'failed'
                online_payment.error_message = 'Payment requires payment method'
            
            else:
                online_payment.status = 'processing'
            
            online_payment.gateway_response = payment_intent.to_dict()
            online_payment.save()
            stripe_payment.save()
            
            payment_serializer = self.get_serializer(online_payment)
            return Response(payment_serializer.data)
            
        except StripePayment.DoesNotExist:
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def completed(self, request):
        """Get all completed payments"""
        completed = self.queryset.filter(status='completed')
        serializer = self.get_serializer(completed, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def failed(self, request):
        """Get all failed payments"""
        failed = self.queryset.filter(status='failed')
        serializer = self.get_serializer(failed, many=True)
        return Response(serializer.data)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """
    Webhook endpoint for Stripe events
    """
    stripe_api_key = os.getenv('STRIPE_SECRET_KEY')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    if not stripe_api_key or not webhook_secret:
        return HttpResponse(status=400)
    
    import stripe
    stripe.api_key = stripe_api_key
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        
        # Update payment record
        try:
            stripe_payment = StripePayment.objects.get(
                stripe_payment_intent_id=payment_intent.id
            )
            online_payment = stripe_payment.online_payment
            
            online_payment.status = 'completed'
            online_payment.completed_at = timezone.now()
            online_payment.gateway_response = payment_intent
            online_payment.save()
            
        except StripePayment.DoesNotExist:
            pass
    
    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        
        try:
            stripe_payment = StripePayment.objects.get(
                stripe_payment_intent_id=payment_intent.id
            )
            online_payment = stripe_payment.online_payment
            
            online_payment.status = 'failed'
            online_payment.error_message = payment_intent.last_payment_error.message if payment_intent.last_payment_error else 'Payment failed'
            online_payment.gateway_response = payment_intent
            online_payment.save()
            
        except StripePayment.DoesNotExist:
            pass
    
    return HttpResponse(status=200)
