from django.contrib import admin
from .models import InstallmentPlan, InstallmentPayment


class InstallmentPaymentInline(admin.TabularInline):
    model = InstallmentPayment
    extra = 0
    readonly_fields = ['is_overdue', 'days_overdue']
    fields = ['installment_number', 'amount', 'due_date', 'payment_date', 'status', 'payment_method']


@admin.register(InstallmentPlan)
class InstallmentPlanAdmin(admin.ModelAdmin):
    list_display = ['patient', 'total_amount', 'number_of_installments', 'status', 'start_date', 'is_delinquent']
    list_filter = ['status', 'start_date']
    search_fields = ['patient__first_name', 'patient__last_name']
    ordering = ['-created_at']
    date_hierarchy = 'start_date'
    inlines = [InstallmentPaymentInline]
    
    fieldsets = (
        ('Paciente', {
            'fields': ('patient', 'budget')
        }),
        ('Detalles del Plan', {
            'fields': ('total_amount', 'number_of_installments', 'installment_amount', 'start_date')
        }),
        ('Estado', {
            'fields': ('status', 'notes')
        }),
    )
    
    def is_delinquent(self, obj):
        return obj.is_delinquent
    is_delinquent.boolean = True
    is_delinquent.short_description = 'Moroso'


@admin.register(InstallmentPayment)
class InstallmentPaymentAdmin(admin.ModelAdmin):
    list_display = ['installment_plan', 'installment_number', 'amount', 'due_date', 'payment_date', 'status', 'is_overdue']
    list_filter = ['status', 'payment_method', 'due_date']
    search_fields = ['installment_plan__patient__first_name', 'installment_plan__patient__last_name']
    ordering = ['due_date']
    date_hierarchy = 'due_date'
    
    fieldsets = (
        ('Plan de Cuotas', {
            'fields': ('installment_plan', 'installment_number')
        }),
        ('Detalles del Pago', {
            'fields': ('amount', 'due_date', 'payment_date', 'status', 'payment_method')
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
    )
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Vencido'
