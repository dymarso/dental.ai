# Backend Models Enhancement Documentation

## Overview
This document describes all the enhancements made to the Dental Practice Management System backend models.

## Changes Summary

### 1. Patient Model Enhancements
**File:** `backend/patients/models.py`

**New Fields:**
- `uuid` (UUIDField): Unique identifier for each patient
- `patient_number` (CharField): Auto-generated patient number (format: PAT-YYYYMMDD-XXXX)
- `emergency_contact_name` (CharField): Emergency contact person name
- `emergency_contact_phone` (CharField): Emergency contact phone number
- `emergency_contact_relationship` (CharField): Relationship to patient
- `is_deleted` (BooleanField): Soft delete flag
- `deleted_at` (DateTimeField): Timestamp when patient was soft-deleted

**New Features:**
- Custom `PatientManager` with soft delete support
  - `objects.all()` - Excludes deleted patients by default
  - `objects.all_with_deleted()` - Returns all patients including deleted
  - `objects.deleted_only()` - Returns only deleted patients
- Auto-generation of `patient_number` on save
- Soft delete methods: `soft_delete()` and `restore()`

**Serializer Updates:** `backend/patients/serializers.py`
- Added new fields to `PatientSerializer`

**View Updates:** `backend/patients/views.py`
- Added `soft_delete` action endpoint (POST /api/patients/{id}/soft_delete/)
- Added `restore` action endpoint (POST /api/patients/{id}/restore/)
- Updated filterset to include `is_deleted` field
- Updated search to include `patient_number`

**Admin Updates:** `backend/patients/admin.py`
- Added `patient_number` and `uuid` to list display
- Added emergency contact fields to fieldsets
- Added soft delete admin actions

---

### 2. Appointment Model Enhancements
**File:** `backend/appointments/models.py`

**New Fields:**
- `telemedicine_enabled` (BooleanField): Indicates if telemedicine is enabled
- `video_link` (URLField): Video conferencing link for telemedicine
- `public_booking` (BooleanField): Indicates if booked via public booking system
- `created_by` (CharField): Username of the user who created the appointment

**New Methods:**
- `is_within_business_hours()`: Validates appointment is between 8 AM - 8 PM
- `has_conflicts()`: Checks for conflicting appointments
- `clean()`: Custom validation including business hours and conflict detection

**Serializer Updates:** `backend/appointments/serializers.py`
- Added new fields to `AppointmentSerializer`
- Added validation methods for business hours and conflicts

**View Updates:** `backend/appointments/views.py`
- Added `agenda` endpoint (GET /api/appointments/agenda/?view=daily|weekly&date=YYYY-MM-DD)
  - Daily view: Returns all appointments for a specific date
  - Weekly view: Returns appointments grouped by day for the week
- Added `public_booking` endpoint (GET/POST /api/appointments/public_booking/)
  - GET: Returns available time slots for a specific date
  - POST: Creates a public booking appointment
- Updated `perform_create` to track `created_by`

**Admin Updates:** `backend/appointments/admin.py`
- Added telemedicine and public booking fields to list display and filters

---

### 3. Clinical Models Enhancements
**File:** `backend/clinical/models.py`

**New Models:**

#### Odontogram Model
- `patient` (ForeignKey): Link to patient
- `tooth_data` (JSONField): Tooth information (supports 20 or 32 teeth)
- `date` (DateField): Date of odontogram
- `notes` (TextField): Additional notes
- `created_by` (CharField): Creator username
- Validates tooth numbers (11-18, 21-28, 31-38, 41-48 for permanent; 51-55, 61-65, 71-75, 81-85 for deciduous)

#### Periodontogram Model
- `patient` (ForeignKey): Link to patient
- `measurements` (JSONField): 6 measurements per tooth (0-15mm range)
- `date` (DateField): Date of periodontogram
- `has_abnormal_values` (BooleanField): Auto-flagged if values > 3mm
- `notes` (TextField): Additional notes
- `created_by` (CharField): Creator username
- Validates measurement ranges and flags abnormal values

**Enhanced ClinicalFile Model:**
- Added file size validation (max 10MB)
- Added file type validation (JPEG, PNG, HEIC, PDF, DOCX)
- Unique filename generation using UUID
- Enhanced `clean()` method for validations
- Enhanced `save()` method for filename generation

**New Files:**
- `backend/clinical/serializers.py`: Serializers for all clinical models
- `backend/clinical/urls.py`: URL routing for clinical endpoints

**View Updates:** `backend/clinical/views.py`
- Added viewsets for all models:
  - `MedicalHistoryViewSet`
  - `ClinicalNoteViewSet`
  - `ClinicalFileViewSet`
  - `OdontogramViewSet`
  - `PeriodontogramViewSet`

**Admin Updates:** `backend/clinical/admin.py`
- Added admin classes for `Odontogram` and `Periodontogram`
- Enhanced existing admin classes

---

### 4. Treatment Models Enhancements
**File:** `backend/treatments/models.py`

**New Models:**

#### OrthodonticCase Model
- `treatment` (OneToOneField): Link to treatment
- `appliance_type` (CharField): Type of orthodontic appliance (metal braces, ceramic, invisalign, etc.)
- `start_date` (DateField): Treatment start date
- `expected_end_date` (DateField): Expected completion date
- `adjustments` (JSONField): Array of adjustment history
- `notes` (TextField): Additional notes
- Method `add_adjustment()`: Add adjustment to history

#### AestheticProcedure Model
- `treatment` (OneToOneField): Link to treatment
- `procedure_type` (CharField): Type of procedure (whitening, veneers, bonding, etc.)
- `product_used` (CharField): Product/brand used
- `before_photo` (ImageField): Before photo
- `after_photo` (ImageField): After photo
- `satisfaction_rating` (PositiveSmallIntegerField): 1-5 star rating
- `completion_date` (DateField): Completion date
- `notes` (TextField): Additional notes
- Validates satisfaction_rating is between 1-5

**Serializer Updates:** `backend/treatments/serializers.py`
- Added `OrthodonticCaseSerializer`
- Added `AestheticProcedureSerializer`
- Updated `TreatmentSerializer` to include related orthodontic and aesthetic data

**View Updates:** `backend/treatments/views.py`
- Added `OrthodonticCaseViewSet` with `add_adjustment` action
- Added `AestheticProcedureViewSet`

**URL Updates:** `backend/treatments/urls.py`
- Added routes for orthodontic-cases and aesthetic-procedures

**Admin Updates:** `backend/treatments/admin.py`
- Added admin classes for `OrthodonticCase` and `AestheticProcedure`

---

### 5. Budget Model Enhancements
**File:** `backend/budgets/models.py`

**New Fields:**
- `budget_number` (CharField): Auto-generated budget number (format: BUD-YYYYMMDD-XXXX)
- `version` (PositiveIntegerField): Version number for budget revisions
- `parent_budget` (ForeignKey): Link to previous version (for versioning)

**New Methods:**
- `_generate_budget_number()`: Generates unique budget number
- `create_new_version(user)`: Creates a new version of the budget
- `generate_pdf()`: Generates PDF using reportlab with:
  - Budget header with number, patient info, dates
  - Items table with treatments, quantities, prices
  - Total amount
  - Notes section

**Serializer Updates:** `backend/budgets/serializers.py`
- Added `budget_number` to read-only fields

**View Updates:** `backend/budgets/views.py`
- Added `create_version` action (POST /api/budgets/{id}/create_version/)
- Added `generate_pdf` action (GET /api/budgets/{id}/generate_pdf/)
  - Returns PDF file as downloadable attachment

**Admin Updates:** `backend/budgets/admin.py`
- Added `budget_number` and `version` to list display
- Added readonly fields for auto-generated values

---

## Database Migrations Required

To apply these changes, run the following commands:

```bash
# Navigate to backend directory
cd backend

# Create migrations for each app
python manage.py makemigrations patients
python manage.py makemigrations appointments
python manage.py makemigrations clinical
python manage.py makemigrations treatments
python manage.py makemigrations budgets

# Apply all migrations
python manage.py migrate
```

## New API Endpoints

### Patients
- `POST /api/patients/{id}/soft_delete/` - Soft delete a patient
- `POST /api/patients/{id}/restore/` - Restore a soft-deleted patient
- `GET /api/patients/?include_deleted=true` - List all patients including deleted

### Appointments
- `GET /api/appointments/agenda/?view=daily&date=YYYY-MM-DD` - Get daily agenda
- `GET /api/appointments/agenda/?view=weekly&date=YYYY-MM-DD` - Get weekly agenda
- `GET /api/appointments/public_booking/?date=YYYY-MM-DD` - Get available slots
- `POST /api/appointments/public_booking/` - Create public booking

### Clinical
- `GET/POST /api/clinical/odontograms/` - Manage odontograms
- `GET/POST /api/clinical/periodontograms/` - Manage periodontograms
- All standard CRUD endpoints for medical histories, clinical notes, and files

### Treatments
- `GET/POST /api/treatments/orthodontic-cases/` - Manage orthodontic cases
- `POST /api/treatments/orthodontic-cases/{id}/add_adjustment/` - Add adjustment
- `GET/POST /api/treatments/aesthetic-procedures/` - Manage aesthetic procedures

### Budgets
- `POST /api/budgets/{id}/create_version/` - Create new budget version
- `GET /api/budgets/{id}/generate_pdf/` - Generate and download PDF

## Dependencies

All required dependencies are already in `backend/_config/requirements/base.txt`:
- `reportlab==4.1.0` - For PDF generation
- `Pillow>=10.3.0` - For image handling

## Backward Compatibility

All changes maintain backward compatibility:
- New fields have `null=True` or default values
- Existing fields are unchanged
- Custom managers don't break existing queries
- Auto-increment ID fields remain as primary keys alongside UUID

## Testing Recommendations

1. **Patient Model:**
   - Test patient number generation
   - Test soft delete and restore functionality
   - Test emergency contact fields

2. **Appointment Model:**
   - Test business hours validation
   - Test conflict detection
   - Test telemedicine fields
   - Test public booking flow
   - Test agenda endpoints

3. **Clinical Models:**
   - Test odontogram with different tooth numbers
   - Test periodontogram validation and abnormal value flagging
   - Test file upload with size/type restrictions

4. **Treatment Models:**
   - Test orthodontic case creation and adjustment tracking
   - Test aesthetic procedure with photos and ratings

5. **Budget Model:**
   - Test budget number generation
   - Test version creation
   - Test PDF generation

## Security Considerations

1. **File Uploads:**
   - Max file size enforced (10MB)
   - File type validation (JPEG, PNG, HEIC, PDF, DOCX)
   - Unique filename generation to prevent overwrites

2. **Soft Delete:**
   - Deleted patients excluded by default
   - Separate method to access deleted records
   - Audit trail with deleted_at timestamp

3. **Public Booking:**
   - Business hours validation
   - Conflict detection to prevent double-booking
   - Creator tracking for audit purposes

## Spanish Verbose Names

All models maintain Spanish verbose names as per project conventions:
- Field labels in Spanish
- Model verbose names in Spanish
- Admin interface in Spanish
- Help text in Spanish
