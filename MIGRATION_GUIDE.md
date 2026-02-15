# Migration Guide for Backend Model Enhancements

## Pre-Migration Checklist

Before running migrations, ensure:

1. ✓ Backup your database
2. ✓ All dependencies are installed
3. ✓ You have database credentials set up
4. ✓ The application is in maintenance mode (if in production)

## Step-by-Step Migration Instructions

### 1. Install Dependencies

Ensure all required packages are installed:

```bash
pip install -r backend/_config/requirements/base.txt
```

Key dependencies for new features:
- `reportlab==4.1.0` - PDF generation
- `Pillow>=10.3.0` - Image handling
- `Django==4.2.7` - Core framework

### 2. Environment Setup

Set required environment variables:

```bash
export DOMAIN=your-domain.com
export DATABASE_URL=your-database-url
export SECRET_KEY=your-secret-key
```

For local development:
```bash
export DOMAIN=localhost
export DEBUG=True
export DATABASE_URL=postgresql://user:password@localhost:5432/dientex
```

### 3. Create Migrations

Navigate to the backend directory and create migrations for each app:

```bash
cd backend

# Patients app - UUID, patient_number, soft delete, emergency contacts
python manage.py makemigrations patients

# Appointments app - telemedicine, public booking, business hours validation
python manage.py makemigrations appointments

# Clinical app - Odontogram, Periodontogram, enhanced file validation
python manage.py makemigrations clinical

# Treatments app - OrthodonticCase, AestheticProcedure
python manage.py makemigrations treatments

# Budgets app - budget_number, versioning, PDF generation
python manage.py makemigrations budgets
```

### 4. Review Migrations

Review the generated migration files in each app's `migrations/` directory to ensure they're correct.

### 5. Apply Migrations

Apply all migrations:

```bash
python manage.py migrate
```

Or apply app-by-app:

```bash
python manage.py migrate patients
python manage.py migrate appointments
python manage.py migrate clinical
python manage.py migrate treatments
python manage.py migrate budgets
```

### 6. Post-Migration Tasks

#### A. Update Existing Patients (Optional)

If you have existing patients without `patient_number`, you can generate them:

```python
# Run in Django shell: python manage.py shell

from patients.models import Patient
from django.utils import timezone

# Get patients without patient_number
patients = Patient.objects.all_with_deleted().filter(patient_number__isnull=True)

for patient in patients:
    patient.save()  # This will trigger patient_number generation
    print(f"Generated patient_number for {patient.full_name}: {patient.patient_number}")
```

#### B. Update Existing Budgets (Optional)

If you have existing budgets without `budget_number`:

```python
# Run in Django shell: python manage.py shell

from budgets.models import Budget

budgets = Budget.objects.filter(budget_number__isnull=True)

for budget in budgets:
    budget.save()  # This will trigger budget_number generation
    print(f"Generated budget_number for budget ID {budget.id}: {budget.budget_number}")
```

#### C. Create Media Directories

Ensure media directories exist for file uploads:

```bash
mkdir -p media/clinical_files
mkdir -p media/treatment_files
mkdir -p media/aesthetic_procedures/before
mkdir -p media/aesthetic_procedures/after
```

### 7. Verify Installation

Run these verification steps:

#### A. Check Models

```bash
python manage.py check
```

#### B. Test Model Creation

```python
# Run in Django shell: python manage.py shell

# Test Patient
from patients.models import Patient
from datetime import date

patient = Patient.objects.create(
    first_name="Test",
    last_name="Patient",
    gender="M",
    date_of_birth=date(1990, 1, 1),
    phone="+1234567890",
    emergency_contact_name="Jane Doe",
    emergency_contact_phone="+0987654321",
    emergency_contact_relationship="Spouse"
)
print(f"Patient created: {patient.patient_number}")
patient.delete()  # Clean up

# Test Appointment business hours validation
from appointments.models import Appointment
from datetime import time, date, timedelta

try:
    appointment = Appointment(
        patient=patient,
        consultation_type="first_visit",
        date=date.today() + timedelta(days=1),
        start_time=time(22, 0),  # 10 PM - should fail
        end_time=time(23, 0),
        status="pending"
    )
    appointment.save()
except Exception as e:
    print(f"✓ Business hours validation working: {e}")

# Test Odontogram
from clinical.models import Odontogram

odontogram = Odontogram.objects.create(
    patient=patient,
    date=date.today(),
    tooth_data={
        "11": {"condition": "healthy"},
        "21": {"condition": "cavity"}
    }
)
print(f"✓ Odontogram created: {odontogram}")
odontogram.delete()

# Test Periodontogram
from clinical.models import Periodontogram

periodontogram = Periodontogram.objects.create(
    patient=patient,
    date=date.today(),
    measurements={
        "11": [1, 2, 1, 2, 1, 2],  # Normal values
        "21": [4, 5, 4, 3, 4, 5]   # Abnormal values (>3mm)
    }
)
print(f"✓ Periodontogram created with abnormal flag: {periodontogram.has_abnormal_values}")
periodontogram.delete()

# Test Budget PDF generation
from budgets.models import Budget, BudgetItem

budget = Budget.objects.create(
    patient=patient,
    title="Test Budget",
    status="pending"
)
print(f"✓ Budget created: {budget.budget_number}")

BudgetItem.objects.create(
    budget=budget,
    treatment_type="Cleaning",
    quantity=1,
    unit_price=100
)

pdf = budget.generate_pdf()
print(f"✓ PDF generated: {len(pdf)} bytes")

budget.delete()
```

### 8. Update URL Configuration

Ensure the clinical app URLs are included in the main URL configuration.

Check `backend/_config/urls.py` includes:

```python
path('api/clinical/', include('clinical.urls')),
```

### 9. Collect Static Files (Production)

If deploying to production:

```bash
python manage.py collectstatic --noinput
```

### 10. Test API Endpoints

Use curl or a tool like Postman to test the new endpoints:

```bash
# Test patient soft delete
curl -X POST http://localhost:8000/api/patients/1/soft_delete/

# Test agenda endpoint
curl http://localhost:8000/api/appointments/agenda/?view=daily&date=2024-02-15

# Test budget PDF generation
curl http://localhost:8000/api/budgets/1/generate_pdf/ --output budget.pdf
```

## Rollback Plan

If you need to rollback migrations:

```bash
# Rollback to previous migration
python manage.py migrate patients <previous_migration_name>
python manage.py migrate appointments <previous_migration_name>
python manage.py migrate clinical <previous_migration_name>
python manage.py migrate treatments <previous_migration_name>
python manage.py migrate budgets <previous_migration_name>

# Or rollback all
python manage.py migrate patients zero  # WARNING: This will delete all data!
```

## Troubleshooting

### Issue: "Apps aren't loaded yet"
**Solution:** Ensure Django settings are properly configured and all dependencies are installed.

### Issue: Migration conflicts
**Solution:** 
```bash
python manage.py makemigrations --merge
```

### Issue: "Module not found"
**Solution:** Check all imports and ensure the app is in `INSTALLED_APPS`.

### Issue: File upload errors
**Solution:** 
- Check media directories exist and have proper permissions
- Verify MEDIA_ROOT and MEDIA_URL settings
- Check file size and type validations

### Issue: PDF generation fails
**Solution:**
- Ensure reportlab is installed: `pip install reportlab`
- Check that font files are accessible
- Verify sufficient memory for PDF generation

## Performance Considerations

1. **Database Indexes:**
   - UUID fields are indexed automatically
   - patient_number has unique index
   - budget_number has unique index

2. **QuerySet Optimization:**
   - Use `select_related()` for foreign keys
   - Use `prefetch_related()` for reverse foreign keys
   - Example: `Patient.objects.select_related('medical_history')`

3. **File Storage:**
   - Consider using cloud storage (GCS, S3) for production
   - Implement CDN for serving media files
   - Set up file cleanup tasks for old files

## Monitoring and Logging

After migration, monitor:

1. Database query performance
2. File upload sizes and storage usage
3. PDF generation performance
4. Soft delete queries (ensure using correct manager)

## Support and Documentation

For more information, see:
- `ENHANCEMENTS_DOCUMENTATION.md` - Detailed feature documentation
- Django docs: https://docs.djangoproject.com/
- Project README: `README.md`

## Completion Checklist

- [ ] Backup created
- [ ] Dependencies installed
- [ ] Migrations created
- [ ] Migrations reviewed
- [ ] Migrations applied
- [ ] Patient numbers generated for existing records
- [ ] Budget numbers generated for existing records
- [ ] Media directories created
- [ ] Models verified with `python manage.py check`
- [ ] Test cases run successfully
- [ ] API endpoints tested
- [ ] Static files collected (production)
- [ ] Documentation updated
- [ ] Team notified of new features
