# Backend Modules Documentation

## Implemented Modules

This document provides a quick reference for the newly implemented backend modules for the Dental Practice Management System.

## 1. Authentication (`/api/authentication/`)

### Endpoints:
```
POST   /api/authentication/login/        # Login with username/password
POST   /api/authentication/logout/       # Logout and revoke token
POST   /api/authentication/refresh/      # Refresh access token
GET    /api/authentication/me/           # Get current user info
POST   /api/authentication/register/     # Register new user
```

### Usage Example:
```javascript
// Login
const response = await fetch('/api/authentication/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'password' })
});
const { user, tokens } = await response.json();

// Use token in subsequent requests
fetch('/api/patients/', {
  headers: { 'Authorization': `Bearer ${tokens.access}` }
});
```

## 2. Installments (`/api/installments/`)

### Endpoints:
```
# Plans
GET/POST  /api/installments/plans/
GET       /api/installments/plans/{id}/
POST      /api/installments/plans/{id}/cancel/
GET       /api/installments/plans/delinquent/

# Payments
GET/POST  /api/installments/payments/
POST      /api/installments/payments/{id}/mark_paid/
GET       /api/installments/payments/overdue/
GET       /api/installments/payments/upcoming/
```

### Create Installment Plan:
```javascript
const plan = {
  patient: 1,
  budget: 2,
  total_amount: 10000.00,
  number_of_installments: 12,
  installment_amount: 833.33,
  start_date: '2024-01-01'
};
```

## 3. Notifications (`/api/notifications/`)

### Endpoints:
```
GET/POST  /api/notifications/
POST      /api/notifications/{id}/send/
POST      /api/notifications/send_bulk/
GET       /api/notifications/pending/
GET       /api/notifications/failed/
POST      /api/notifications/{id}/retry/
```

### Send Notification:
```javascript
const notification = {
  patient: 1,
  notification_type: 'appointment_reminder',
  method: 'whatsapp',
  subject: 'Recordatorio de Cita',
  message: 'Tiene una cita mañana a las 10:00 AM'
};
```

## 4. Agreements (`/api/agreements/`)

### Endpoints:
```
GET/POST  /api/agreements/
GET       /api/agreements/{id}/
POST      /api/agreements/{id}/sign/
POST      /api/agreements/{id}/decline/
GET       /api/agreements/{id}/download_pdf/
GET       /api/agreements/pending/
GET       /api/agreements/signed/
```

### Sign Agreement:
```javascript
const signature = {
  signature_data: 'data:image/png;base64,...',
  signed_by_name: 'Juan Pérez'
};

await fetch(`/api/agreements/${agreementId}/sign/`, {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(signature)
});
```

## 5. Online Payments (`/api/online_payments/`)

### Endpoints:
```
GET/POST  /api/online_payments/
POST      /api/online_payments/create_payment_intent/
POST      /api/online_payments/confirm_payment/
GET       /api/online_payments/completed/
GET       /api/online_payments/failed/
POST      /api/online_payments/webhook/stripe/
```

### Stripe Payment Flow:
```javascript
// 1. Create payment intent
const { client_secret } = await fetch('/api/online_payments/create_payment_intent/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    patient_id: 1,
    amount: 500.00,
    currency: 'mxn'
  })
}).then(r => r.json());

// 2. Use Stripe.js to collect payment
const stripe = Stripe('pk_...');
const { paymentIntent } = await stripe.confirmCardPayment(client_secret);

// 3. Confirm on backend
await fetch('/api/online_payments/confirm_payment/', {
  method: 'POST',
  body: JSON.stringify({ payment_intent_id: paymentIntent.id })
});
```

## Environment Variables

Add these to your `.env` or Docker environment:

```bash
# SendGrid (Email)
SENDGRID_API_KEY=your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Twilio (SMS/WhatsApp)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Running Migrations

```bash
# Create migrations
docker compose -f development.yml exec backend python manage.py makemigrations

# Apply migrations
docker compose -f development.yml exec backend python manage.py migrate

# Create superuser (if needed)
docker compose -f development.yml exec backend python manage.py createsuperuser
```

## Admin Access

Access Django admin at: `http://localhost/admin/`

All models are available in the admin interface with:
- Custom list views
- Search and filter capabilities
- Inline editing
- Bulk actions

## Testing

Test endpoints using curl:

```bash
# Login
curl -X POST http://localhost/api/authentication/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'

# Get patients (with token)
curl http://localhost/api/patients/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Notes

- All apps are automatically discovered by Django (no need to add to INSTALLED_APPS)
- URLs are automatically registered under `/api/<app_name>/`
- JWT tokens expire after 1 hour (access) and 7 days (refresh)
- Notifications require external API keys (SendGrid, Twilio)
- Payments require Stripe API keys
- Celery tasks are available but require Celery worker setup

---

For more details, see the full implementation summary in `IMPLEMENTATION_SUMMARY.md`
