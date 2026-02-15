from django.contrib import admin
from .models import OnlinePayment, StripePayment


class StripePaymentInline(admin.StackedInline):
    model = StripePayment
    extra = 0
    readonly_fields = ['stripe_payment_intent_id', 'stripe_customer_id', 'stripe_charge_id',
                       'card_brand', 'card_last4', 'card_exp_month', 'card_exp_year']


@admin.register(OnlinePayment)
class OnlinePaymentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'amount', 'currency', 'payment_method', 'status', 'payment_date', 'completed_at']
    list_filter = ['payment_method', 'status', 'currency', 'payment_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'transaction_id', 'customer_email']
    ordering = ['-created_at']
    date_hierarchy = 'payment_date'
    readonly_fields = ['transaction_id', 'gateway_response', 'payment_date', 'completed_at', 
                       'created_at', 'updated_at']
    inlines = [StripePaymentInline]
    
    fieldsets = (
        ('Paciente', {
            'fields': ('patient', 'installment_payment')
        }),
        ('Detalles del Pago', {
            'fields': ('amount', 'currency', 'payment_method', 'status')
        }),
        ('Información del Gateway', {
            'fields': ('transaction_id', 'gateway_response')
        }),
        ('Fechas', {
            'fields': ('payment_date', 'completed_at', 'created_at', 'updated_at')
        }),
        ('Cliente', {
            'fields': ('customer_name', 'customer_email')
        }),
        ('Notas', {
            'fields': ('notes', 'error_message')
        }),
    )


@admin.register(StripePayment)
class StripePaymentAdmin(admin.ModelAdmin):
    list_display = ['online_payment', 'stripe_payment_intent_id', 'card_brand', 'card_last4']
    search_fields = ['stripe_payment_intent_id', 'stripe_customer_id', 'stripe_charge_id']
    ordering = ['-created_at']
    readonly_fields = ['stripe_payment_intent_id', 'stripe_customer_id', 'stripe_charge_id',
                       'card_brand', 'card_last4', 'card_exp_month', 'card_exp_year',
                       'created_at', 'updated_at']
    
    fieldsets = (
        ('Pago', {
            'fields': ('online_payment',)
        }),
        ('Stripe IDs', {
            'fields': ('stripe_payment_intent_id', 'stripe_customer_id', 'stripe_charge_id')
        }),
        ('Información de Tarjeta', {
            'fields': ('card_brand', 'card_last4', 'card_exp_month', 'card_exp_year')
        }),
        ('Metadata', {
            'fields': ('stripe_metadata',),
            'classes': ('collapse',)
        }),
    )
