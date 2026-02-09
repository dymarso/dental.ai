# Migration Dependency Fix

## Problem
Django migrations were failing with `InconsistentMigrationHistory` error on both Vercel and Railway deployments:

```
django.db.migrations.exceptions.InconsistentMigrationHistory: 
Migration finances.0001_initial is applied before its dependency 
patients.0001_initial on database 'default'.
```

## Root Cause
All initial migration files were generated at the same timestamp (2026-02-08 11:42), causing Django to potentially apply them in the wrong order in the database's `django_migrations` table.

## Solution

### 1. Migration Timestamp Ordering
Updated migration file timestamps to reflect the correct dependency chain:

- **11:40** - `patients` (no dependencies)
- **11:41** - `treatments`, `appointments`, `budgets`, `clinical` (depend on patients)
- **11:42** - `finances` (depends on patients + treatments)

### 2. Automatic Fix in Deployment
The `entrypoint.sh` script now:
1. Detects `InconsistentMigrationHistory` errors during deployment
2. Automatically fixes the `django_migrations` table by:
   - Removing incorrectly ordered migration records
   - Re-inserting them in the correct dependency order
3. Retries the migration

### 3. Manual Fix Command
A management command is available for manual fixes:

```bash
# Dry run (preview changes)
python manage.py fix_migration_history

# Actually apply the fix
python manage.py fix_migration_history --apply
```

## Testing the Fix

### Fresh Database
For a fresh database, the timestamp ordering ensures migrations are applied correctly from the start.

### Existing Database with Wrong Order
For databases that already have migrations in the wrong order, the entrypoint script will automatically detect and fix the issue during deployment.

## Files Changed
- `backend/patients/migrations/0001_initial.py` - Updated timestamp
- `backend/treatments/migrations/0001_initial.py` - Updated timestamp
- `backend/appointments/migrations/0001_initial.py` - Updated timestamp
- `backend/budgets/migrations/0001_initial.py` - Updated timestamp
- `backend/clinical/migrations/0001_initial.py` - Updated timestamp
- `backend/_config/entrypoint.sh` - Added automatic fix logic
- `backend/patients/management/commands/fix_migration_history.py` - New manual fix command
