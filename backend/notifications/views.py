from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    BulkNotificationSerializer
)
from .services import send_notification


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notifications
    """
    queryset = Notification.objects.select_related('patient', 'appointment')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['patient', 'notification_type', 'method', 'status', 'appointment']
    search_fields = ['patient__first_name', 'patient__last_name', 'message']
    ordering_fields = ['created_at', 'sent_at', 'scheduled_for']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send a notification immediately"""
        notification = self.get_object()
        
        if notification.status == 'sent':
            return Response(
                {'error': 'Notification already sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Send notification
        result = send_notification(notification)
        
        serializer = self.get_serializer(notification)
        return Response({
            'notification': serializer.data,
            'send_result': result
        })
    
    @action(detail=False, methods=['post'])
    def send_bulk(self, request):
        """Send bulk notifications to multiple patients"""
        serializer = BulkNotificationSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        from patients.models import Patient
        
        patient_ids = serializer.validated_data['patients']
        notification_type = serializer.validated_data['notification_type']
        method = serializer.validated_data['method']
        subject = serializer.validated_data.get('subject', '')
        message = serializer.validated_data['message']
        scheduled_for = serializer.validated_data.get('scheduled_for')
        
        # Get patients
        patients = Patient.objects.filter(id__in=patient_ids)
        
        notifications_created = []
        for patient in patients:
            # Determine recipient based on method
            recipient_email = patient.email if method == 'email' else None
            recipient_phone = patient.phone if method in ['sms', 'whatsapp'] else None
            
            # Skip if patient doesn't have required contact info
            if method == 'email' and not recipient_email:
                continue
            if method in ['sms', 'whatsapp'] and not recipient_phone:
                continue
            
            # Create notification
            notification = Notification.objects.create(
                patient=patient,
                notification_type=notification_type,
                method=method,
                subject=subject,
                message=message,
                recipient_email=recipient_email,
                recipient_phone=recipient_phone,
                scheduled_for=scheduled_for,
                status='pending'
            )
            
            # Send immediately if not scheduled
            if not scheduled_for:
                send_notification(notification)
            
            notifications_created.append(notification)
        
        serializer = self.get_serializer(notifications_created, many=True)
        return Response({
            'count': len(notifications_created),
            'notifications': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending notifications"""
        pending = self.queryset.filter(status='pending')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def failed(self, request):
        """Get all failed notifications"""
        failed = self.queryset.filter(status='failed')
        serializer = self.get_serializer(failed, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry sending a failed notification"""
        notification = self.get_object()
        
        if notification.status != 'failed':
            return Response(
                {'error': 'Only failed notifications can be retried'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset status
        notification.status = 'pending'
        notification.error_message = None
        notification.save()
        
        # Send notification
        result = send_notification(notification)
        
        serializer = self.get_serializer(notification)
        return Response({
            'notification': serializer.data,
            'send_result': result
        })
