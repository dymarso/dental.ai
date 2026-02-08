# Django Migration History Fix

## Problem

The application was experiencing the following error during deployment:

```
django.db.migrations.exceptions.InconsistentMigrationHistory: Migration finances.0001_initial is applied before its dependency patients.0001_initial on database 'default'.
```

This error occurred because:
1. Django apps were being added to `INSTALLED_APPS` in alphabetical order using the `find_apps()` function
2. The `finances` app depends on both `patients` and `treatments` apps
3. Alphabetically, `finances` comes before `patients` and `treatments`
4. This caused migrations to be applied in the wrong order in the database

## Solution

### 1. Fixed INSTALLED_APPS Order (settings.py)

The `INSTALLED_APPS` in `/backend/_config/settings.py` has been updated to explicitly list apps in dependency order:

```python
INSTALLED_APPS = [
    # Django core apps...
    'corsheaders',
    'rest_framework',
    # ... other third-party apps ...
    
    # Custom apps in dependency order
    'patients',      # No dependencies - base app
    'reports',       # No dependencies - independent
    'profiles',      # Depends on Django auth
    'treatments',    # Depends on patients
    'appointments',  # Depends on patients
    'budgets',       # Depends on patients
    'clinical',      # Depends on patients
    'finances',      # Depends on patients and treatments - must be last
]
```

This ensures:
- Fresh databases will have migrations applied in the correct order
- Future migrations will not encounter dependency issues
- Apps are loaded in a predictable, dependency-respecting order

### 2. Fix Script for Existing Databases

For databases that already have inconsistent migration history, use the provided fix script:

#### Usage

**Option A: Run from within the Django container**

```bash
# Access the running container
docker exec -it <container-name> bash

# Run the fix script
/backend/_config/scripts/fix_migration_history.sh
```

**Option B: Railway/Vercel deployment**

For Railway or Vercel, you can run this as a one-time deployment command:

```bash
# In Railway/Vercel console or as a run command
bash /backend/_config/scripts/fix_migration_history.sh
```

#### What the script does

1. **Backs up current migration records** to `/tmp/django_migrations_backup.csv`
2. **Clears all migration records** from the `django_migrations` table
3. **Fakes all migrations** in the correct dependency order:
   - patients → reports → profiles → treatments → appointments → budgets → clinical → finances
4. **Verifies** that all migrations are now properly recorded

#### Important Notes

⚠️ **Before running the fix script:**
- Ensure your database already has all tables created (the schema is correct, only the migration history is wrong)
- Back up your database
- The script is safe because it only modifies the `django_migrations` table, not your actual data tables

✅ **After running the fix script:**
- Verify all migrations show as applied with `python manage.py showmigrations`
- Future migrations will work correctly
- You only need to run this script ONCE

## Migration Dependency Graph

```
patients (base, no deps)
├── treatments
│   └── finances
├── appointments
├── budgets
├── clinical
└── (finances also depends directly on patients)

reports (independent, no deps)

profiles (depends on Django auth)
```

## Prevention

This issue is now prevented by:
1. Explicit app ordering in `INSTALLED_APPS` instead of dynamic discovery
2. Clear documentation of dependencies
3. Removal of the `find_apps()` function that caused non-deterministic ordering

## Testing

To verify the fix worked:

```bash
# Check migration status
python manage.py showmigrations

# All migrations should show [X] indicating they're applied
# No warnings about inconsistent history should appear
```

## Future Migrations

When creating new apps:
1. Add them to `INSTALLED_APPS` in the correct dependency order
2. Ensure migration dependencies are properly specified in migration files
3. Test migrations on a development database first
