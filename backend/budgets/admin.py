from django.contrib import admin
from .models import Budget, BudgetItem


class BudgetItemInline(admin.TabularInline):
    model = BudgetItem
    extra = 1
    readonly_fields = ['subtotal']


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['budget_number', 'title', 'patient', 'total_amount', 'status', 'version', 'created_date']
    list_filter = ['status', 'created_date', 'version']
    search_fields = ['budget_number', 'title', 'patient__first_name', 'patient__last_name']
    ordering = ['-created_date']
    inlines = [BudgetItemInline]
    readonly_fields = ['budget_number', 'created_at', 'updated_at', 'created_date']


@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ['treatment_type', 'budget', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['budget']
    search_fields = ['treatment_type', 'budget__title']
    readonly_fields = ['subtotal']

