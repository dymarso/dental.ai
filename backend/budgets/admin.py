from django.contrib import admin
from .models import Budget, BudgetItem


class BudgetItemInline(admin.TabularInline):
    model = BudgetItem
    extra = 1


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'patient', 'total_amount', 'status', 'created_date']
    list_filter = ['status', 'created_date']
    search_fields = ['title', 'patient__first_name', 'patient__last_name']
    ordering = ['-created_date']
    inlines = [BudgetItemInline]


@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ['treatment_type', 'budget', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['budget']
    search_fields = ['treatment_type', 'budget__title']
