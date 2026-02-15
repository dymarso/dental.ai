"""
Celery tasks for sending notifications asynchronously
Note: This requires Celery to be configured in the project
"""

try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    # Create a dummy decorator if Celery is not available
    def shared_task(func):
        return func


@shared_task
def send_notification_task(notification_id):
    """
    Celery task to send a notification asynchronously
    """
    from .models import Notification
    from .services import send_notification
    
    try:
        notification = Notification.objects.get(id=notification_id)
        result = send_notification(notification)
        return result
    except Notification.DoesNotExist:
        return {'success': False, 'error': 'Notification not found'}


@shared_task
def send_scheduled_notifications():
    """
    Celery task to send scheduled notifications
    This should be run periodically (e.g., every 5 minutes)
    """
    from django.utils import timezone
    from .models import Notification
    from .services import send_notification
    
    # Get pending notifications that are scheduled to be sent
    now = timezone.now()
    notifications = Notification.objects.filter(
        status='pending',
        scheduled_for__lte=now
    )
    
    results = []
    for notification in notifications:
        result = send_notification(notification)
        results.append({
            'notification_id': notification.id,
            'result': result
        })
    
    return {
        'total': len(results),
        'results': results
    }


@shared_task
def send_appointment_reminders():
    """
    Celery task to send appointment reminders
    This should be run daily
    """
    from django.utils import timezone
    from datetime import timedelta
    from appointments.models import Appointment
    from patients.models import Patient
    from .models import Notification
    from .services import send_notification
    
    # Get appointments for tomorrow
    tomorrow = timezone.now().date() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        date=tomorrow,
        status='scheduled',
        reminder_sent=False
    )
    
    results = []
    for appointment in appointments:
        # Determine notification method based on patient preference
        method = appointment.patient.preferred_contact_method
        
        # Create notification
        message = (
            f"Recordatorio: Tienes una cita mañana {appointment.date} "
            f"a las {appointment.start_time}. "
            f"Tipo: {appointment.get_consultation_type_display()}."
        )
        
        notification = Notification.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            notification_type='appointment_reminder',
            method=method,
            subject='Recordatorio de Cita',
            message=message,
            recipient_email=appointment.patient.email if method == 'email' else None,
            recipient_phone=appointment.patient.phone if method in ['sms', 'whatsapp'] else None,
            status='pending'
        )
        
        # Send notification
        result = send_notification(notification)
        
        if result['success']:
            appointment.reminder_sent = True
            appointment.reminder_sent_at = timezone.now()
            appointment.save()
        
        results.append({
            'appointment_id': appointment.id,
            'notification_id': notification.id,
            'result': result
        })
    
    return {
        'total': len(results),
        'results': results
    }


@shared_task
def send_payment_reminders():
    """
    Celery task to send payment reminders for upcoming installments
    This should be run daily
    """
    from django.utils import timezone
    from datetime import timedelta
    from installments.models import InstallmentPayment
    from .models import Notification
    from .services import send_notification
    
    # Get payments due in 3 days
    reminder_date = timezone.now().date() + timedelta(days=3)
    payments = InstallmentPayment.objects.filter(
        due_date=reminder_date,
        status='pending'
    )
    
    results = []
    for payment in payments:
        patient = payment.installment_plan.patient
        method = patient.preferred_contact_method
        
        # Create notification
        message = (
            f"Recordatorio: Tiene un pago pendiente de ${payment.amount} "
            f"con vencimiento el {payment.due_date}. "
            f"Cuota {payment.installment_number} de {payment.installment_plan.number_of_installments}."
        )
        
        notification = Notification.objects.create(
            patient=patient,
            notification_type='payment_reminder',
            method=method,
            subject='Recordatorio de Pago',
            message=message,
            recipient_email=patient.email if method == 'email' else None,
            recipient_phone=patient.phone if method in ['sms', 'whatsapp'] else None,
            status='pending'
        )
        
        # Send notification
        result = send_notification(notification)
        
        results.append({
            'payment_id': payment.id,
            'notification_id': notification.id,
            'result': result
        })
    
    return {
        'total': len(results),
        'results': results
    }
