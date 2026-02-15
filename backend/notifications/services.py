"""
Services for sending notifications via SendGrid (email) and Twilio (SMS/WhatsApp)
"""
import os
from django.conf import settings


class EmailService:
    """Service for sending emails using SendGrid"""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@dientex.com')
    
    def send_email(self, to_email, subject, message):
        """Send email using SendGrid"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'SendGrid API key not configured'
            }
        
        try:
            # Import SendGrid library
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            # Create message
            mail = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=message
            )
            
            # Send email
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(mail)
            
            return {
                'success': True,
                'status_code': response.status_code,
                'message_id': response.headers.get('X-Message-Id')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class SMSService:
    """Service for sending SMS using Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    def send_sms(self, to_phone, message):
        """Send SMS using Twilio"""
        if not self.account_sid or not self.auth_token:
            return {
                'success': False,
                'error': 'Twilio credentials not configured'
            }
        
        try:
            # Import Twilio library
            from twilio.rest import Client
            
            # Create client
            client = Client(self.account_sid, self.auth_token)
            
            # Send SMS
            message_obj = client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_phone
            )
            
            return {
                'success': True,
                'sid': message_obj.sid,
                'status': message_obj.status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class WhatsAppService:
    """Service for sending WhatsApp messages using Twilio"""
    
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
    
    def send_whatsapp(self, to_phone, message):
        """Send WhatsApp message using Twilio"""
        if not self.account_sid or not self.auth_token:
            return {
                'success': False,
                'error': 'Twilio credentials not configured'
            }
        
        try:
            # Import Twilio library
            from twilio.rest import Client
            
            # Create client
            client = Client(self.account_sid, self.auth_token)
            
            # Format phone number for WhatsApp
            to_number = f"whatsapp:{to_phone}"
            
            # Send WhatsApp message
            message_obj = client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            return {
                'success': True,
                'sid': message_obj.sid,
                'status': message_obj.status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


def send_notification(notification):
    """
    Send notification using appropriate service
    Returns response data
    """
    from django.utils import timezone
    
    if notification.method == 'email':
        service = EmailService()
        result = service.send_email(
            notification.recipient_email,
            notification.subject,
            notification.message
        )
    
    elif notification.method == 'sms':
        service = SMSService()
        result = service.send_sms(
            notification.recipient_phone,
            notification.message
        )
    
    elif notification.method == 'whatsapp':
        service = WhatsAppService()
        result = service.send_whatsapp(
            notification.recipient_phone,
            notification.message
        )
    
    else:
        result = {
            'success': False,
            'error': f'Unsupported notification method: {notification.method}'
        }
    
    # Update notification status
    if result['success']:
        notification.status = 'sent'
        notification.sent_at = timezone.now()
        notification.response_data = result
    else:
        notification.status = 'failed'
        notification.error_message = result.get('error', 'Unknown error')
        notification.response_data = result
    
    notification.save()
    
    return result
