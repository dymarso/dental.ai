#!/bin/sh
set -e

echo "🚀 Starting Django production container"

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
    # Handle port: if no colon, use default port 5432
    if [ "$DB_HOST_PORT" = "$PGHOST" ]; then
        export PGPORT="5432"
    else
        export PGPORT="${DB_HOST_PORT#*:}"
    fi
    export PGDATABASE="${DB_HOST_PORT_DB#*/}"
    
    # Remove query parameters (backslash prevents ? from being treated as wildcard)
    export PGDATABASE="${PGDATABASE%%\?*}"
else
    # Use individual environment variables
    export PGHOST="${DB_HOST:-localhost}"
    export PGPORT="${DB_PORT:-5432}"
    export PGDATABASE="${DB_NAME:-postgres}"
    export PGUSER="${DB_USER:-postgres}"
    export PGPASSWORD="${DB_PASSWORD:-postgres}"
fi

# Wait for database to be ready before proceeding
echo "⏳ Waiting for database to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if pg_isready -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" -d "${PGDATABASE}" > /dev/null 2>&1; then
        echo "✅ Database is ready!"
        break
    fi
    attempt=$((attempt + 1))
    echo "   Waiting for database... (attempt ${attempt}/${max_attempts})"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ ERROR: Database not ready after ${max_attempts} attempts"
    echo "   Host: ${PGHOST}, Port: ${PGPORT}, Database: ${PGDATABASE}"
    echo "   Container will exit. Check database connection and try again."
    exit 1
fi

# Restore from start folder if any backup files exist
echo "🔄 Checking for database restore from GitHub repo..."
if [ -f /backend/_config/backup/backup.sh ]; then
    /backend/_config/backup/backup.sh auto-restore || echo "⚠️ Restore skipped or failed, continuing..."
fi

if [ -f manage.py ]; then
    echo "📦 Applying migrations..."
    migration_output=$(python manage.py migrate --noinput 2>&1)
    migration_status=$?
    
    if [ $migration_status -ne 0 ]; then
        echo "❌ Migration failed! This is a fatal error."
        echo ""
        echo "$migration_output"
        echo ""
        
        # Check if it's an InconsistentMigrationHistory error
        if echo "$migration_output" | grep -q "InconsistentMigrationHistory"; then
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "⚠️  MIGRATION HISTORY INCONSISTENCY DETECTED"
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo ""
            echo "This error occurs when migrations were applied in the wrong order."
            echo ""
            echo "To fix this issue, run the migration fix script:"
            echo "  bash /backend/_config/scripts/fix_migration_history.sh"
            echo ""
            echo "Or manually fix the migration history:"
            echo "  1. Connect to your database"
            echo "  2. Clear migration history: DELETE FROM django_migrations;"
            echo "  3. Fake all migrations in order:"
            echo "     python manage.py migrate --fake patients"
            echo "     python manage.py migrate --fake reports"
            echo "     python manage.py migrate --fake profiles"
            echo "     python manage.py migrate --fake treatments"
            echo "     python manage.py migrate --fake appointments"
            echo "     python manage.py migrate --fake budgets"
            echo "     python manage.py migrate --fake clinical"
            echo "     python manage.py migrate --fake finances"
            echo ""
            echo "See /backend/_config/scripts/MIGRATION_FIX_README.md for details."
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        else
            echo "   Database tables are required for the application to work."
            echo "   Please check the database connection and migration files."
        fi
        exit 1
    fi
    echo "✅ Migrations applied successfully"

    echo "📁 Collecting static files..."
    python manage.py collectstatic --noinput --clear || echo "⚠️ Static collection failed, continuing..."

    # Create superuser if not exists
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DOMAIN" ]; then
        python manage.py shell << END
import os
from django.contrib.auth import get_user_model
User = get_user_model()

username = os.getenv('DJANGO_SUPERUSER_USERNAME')
domain = os.getenv('DOMAIN')
email = f'{username}@{domain}'

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, os.getenv('DJANGO_SUPERUSER_PASSWORD'))
    print(f"Superuser created: {username} with email: {email}")
else:
    print(f"Superuser already exists: {username}")
END
    else
        echo "Missing required environment variables for superuser creation"
    fi
fi

exec "$@"
