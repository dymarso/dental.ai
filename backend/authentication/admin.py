from django.contrib import admin
from .models import RefreshToken, AuditLog


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'expires_at', 'revoked', 'is_expired']
    list_filter = ['revoked', 'created_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'jti']
    readonly_fields = ['token', 'jti', 'created_at', 'revoked_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Token', {
            'fields': ('user', 'token', 'jti')
        }),
        ('Fechas', {
            'fields': ('created_at', 'expires_at', 'revoked_at')
        }),
        ('Estado', {
            'fields': ('revoked',)
        }),
    )
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expirado'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['username', 'action', 'resource_type', 'resource_id', 'ip_address', 'timestamp']
    list_filter = ['action', 'resource_type', 'timestamp']
    search_fields = ['username', 'user__username', 'resource_type', 'resource_id', 'ip_address']
    readonly_fields = ['user', 'username', 'action', 'resource_type', 'resource_id', 
                       'ip_address', 'user_agent', 'details', 'timestamp']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'username', 'ip_address', 'user_agent')
        }),
        ('Acción', {
            'fields': ('action', 'resource_type', 'resource_id', 'timestamp')
        }),
        ('Detalles', {
            'fields': ('details',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual creation of audit logs
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of audit logs
        return False
