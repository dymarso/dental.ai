from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['patient', 'notification_type', 'method', 'status', 'scheduled_for', 'sent_at']
    list_filter = ['notification_type', 'method', 'status', 'created_at']
    search_fields = ['patient__first_name', 'patient__last_name', 'message']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['sent_at', 'response_data', 'error_message', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Paciente', {
            'fields': ('patient', 'appointment')
        }),
        ('Detalles de Notificación', {
            'fields': ('notification_type', 'method', 'subject', 'message')
        }),
        ('Destinatario', {
            'fields': ('recipient_email', 'recipient_phone')
        }),
        ('Estado y Programación', {
            'fields': ('status', 'scheduled_for', 'sent_at')
        }),
        ('Respuesta', {
            'fields': ('response_data', 'error_message'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_sent', 'mark_as_failed', 'retry_failed']
    
    def mark_as_sent(self, request, queryset):
        updated = queryset.update(status='sent')
        self.message_user(request, f'{updated} notificaciones marcadas como enviadas')
    mark_as_sent.short_description = 'Marcar como enviado'
    
    def mark_as_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} notificaciones marcadas como fallidas')
    mark_as_failed.short_description = 'Marcar como fallido'
    
    def retry_failed(self, request, queryset):
        from .services import send_notification
        
        failed_notifications = queryset.filter(status='failed')
        count = 0
        for notification in failed_notifications:
            notification.status = 'pending'
            notification.save()
            send_notification(notification)
            count += 1
        
        self.message_user(request, f'{count} notificaciones reenviadas')
    retry_failed.short_description = 'Reintentar envío'
