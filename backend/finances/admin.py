from django.contrib import admin
from .models import Payment, Expense


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'amount', 'payment_method', 'payment_date', 'treatment']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'reference_number']
    ordering = ['-payment_date']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['description', 'category', 'amount', 'expense_date', 'payment_method']
    list_filter = ['category', 'payment_method', 'expense_date']
    search_fields = ['description', 'supplier', 'invoice_number']
    ordering = ['-expense_date']
