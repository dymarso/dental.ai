#!/bin/bash
# Script to fix inconsistent migration history in production databases
# This script should be run ONCE to fix the migration history issue
# caused by apps being registered in the wrong order

set -e

echo "==================================================================="
echo "Django Migration History Fix Script"
echo "==================================================================="
echo ""
echo "This script will fix the InconsistentMigrationHistory error by:"
echo "1. Deleting all migration records from django_migrations table"
echo "2. Faking all migrations to match the current database schema"
echo ""
echo "⚠️  WARNING: This is a one-time fix for existing databases."
echo "    Only run this if you're experiencing migration history errors."
echo ""
echo "Prerequisites:"
echo "  - Database must already have all tables created"
echo "  - No pending migrations should exist"
echo "  - Backup your database before running this script"
echo ""

# Parse DATABASE_URL to extract connection parameters
if [ -n "$DATABASE_URL" ]; then
    # Remove protocol prefix
    DB_URL_NO_PROTO="${DATABASE_URL#postgres://}"
    DB_URL_NO_PROTO="${DB_URL_NO_PROTO#postgresql://}"
    
    # Extract user and password
    DB_USER_PASS="${DB_URL_NO_PROTO%%@*}"
    export PGUSER="${DB_USER_PASS%%:*}"
    export PGPASSWORD="${DB_USER_PASS#*:}"
    
    # Extract host, port, and database
    DB_HOST_PORT_DB="${DB_URL_NO_PROTO#*@}"
    DB_HOST_PORT="${DB_HOST_PORT_DB%%/*}"
    export PGHOST="${DB_HOST_PORT%%:*}"
    if [ "$DB_HOST_PORT" = "$PGHOST" ]; then
        export PGPORT="5432"
    else
        export PGPORT="${DB_HOST_PORT#*:}"
    fi
    export PGDATABASE="${DB_HOST_PORT_DB#*/}"
    export PGDATABASE="${PGDATABASE%%\?*}"
else
    export PGHOST="${DB_HOST:-localhost}"
    export PGPORT="${DB_PORT:-5432}"
    export PGDATABASE="${DB_NAME:-postgres}"
    export PGUSER="${DB_USER:-postgres}"
    export PGPASSWORD="${DB_PASSWORD:-postgres}"
fi

echo "Database Connection:"
echo "  Host: ${PGHOST}"
echo "  Port: ${PGPORT}"
echo "  Database: ${PGDATABASE}"
echo "  User: ${PGUSER}"
echo ""

# Check if running in interactive mode
if [ -t 0 ]; then
    read -p "Do you want to proceed? (yes/no): " -r
    echo
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Aborted."
        exit 1
    fi
else
    echo "Running in non-interactive mode. Proceeding automatically..."
fi

echo ""
echo "Step 1: Checking database connection..."
if pg_isready -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" > /dev/null 2>&1; then
    echo "✅ Database is ready!"
else
    echo "❌ Cannot connect to database!"
    exit 1
fi

echo ""
echo "Step 2: Backing up current migration records..."
psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" -c "\COPY (SELECT * FROM django_migrations) TO '/tmp/django_migrations_backup.csv' CSV HEADER;" || echo "⚠️ Backup failed, continuing anyway..."

echo ""
echo "Step 3: Clearing migration history from database..."
psql -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" -c "DELETE FROM django_migrations;" || {
    echo "❌ Failed to delete migration records!"
    exit 1
}
echo "✅ Migration history cleared"

echo ""
echo "Step 4: Faking all migrations to match current schema..."
cd /backend

# Fake migrations in the correct dependency order
python manage.py migrate --fake patients || {
    echo "❌ Failed to fake patients migrations!"
    exit 1
}

python manage.py migrate --fake reports || {
    echo "❌ Failed to fake reports migrations!"
    exit 1
}

python manage.py migrate --fake profiles || {
    echo "❌ Failed to fake profiles migrations!"
    exit 1
}

python manage.py migrate --fake treatments || {
    echo "❌ Failed to fake treatments migrations!"
    exit 1
}

python manage.py migrate --fake appointments || {
    echo "❌ Failed to fake appointments migrations!"
    exit 1
}

python manage.py migrate --fake budgets || {
    echo "❌ Failed to fake budgets migrations!"
    exit 1
}

python manage.py migrate --fake clinical || {
    echo "❌ Failed to fake clinical migrations!"
    exit 1
}

python manage.py migrate --fake finances || {
    echo "❌ Failed to fake finances migrations!"
    exit 1
}

echo ""
echo "Step 5: Verifying migration status..."
python manage.py showmigrations

echo ""
echo "==================================================================="
echo "✅ Migration history has been successfully fixed!"
echo "==================================================================="
echo ""
echo "Next steps:"
echo "1. Verify that all migrations are marked as applied"
echo "2. Test your application to ensure everything works"
echo "3. Future migrations will now work correctly"
echo ""
