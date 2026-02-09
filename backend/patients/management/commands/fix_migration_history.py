"""
Management command to fix migration history inconsistencies.

This command addresses the issue where migrations were applied in the wrong order
in the database, causing InconsistentMigrationHistory errors.
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix migration history by removing and reapplying migration records in correct order'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually apply the fix (default is dry-run)',
        )

    def handle(self, *args, **options):
        apply = options.get('apply', False)
        
        if not apply:
            self.stdout.write(self.style.WARNING(
                'Running in DRY-RUN mode. Use --apply to actually fix the database.'
            ))
        
        with connection.cursor() as cursor:
            # Check if django_migrations table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'django_migrations'
                );
            """)
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                self.stdout.write(self.style.SUCCESS(
                    'Migration table does not exist yet. No fix needed.'
                ))
                return
            
            # Get current migration records for the affected apps
            affected_apps = ['patients', 'treatments', 'finances', 'appointments', 'budgets', 'clinical']
            cursor.execute("""
                SELECT app, name, applied 
                FROM django_migrations 
                WHERE app IN %s AND name = '0001_initial'
                ORDER BY applied;
            """, (tuple(affected_apps),))
            
            current_migrations = cursor.fetchall()
            
            if not current_migrations:
                self.stdout.write(self.style.SUCCESS(
                    'No initial migrations found. Database is clean.'
                ))
                return
            
            self.stdout.write(self.style.WARNING('Current migration order:'))
            for app, name, applied in current_migrations:
                self.stdout.write(f'  {app}.{name} - applied at {applied}')
            
            # Define correct order based on dependencies
            correct_order = [
                'patients',      # No dependencies
                'treatments',    # Depends on patients
                'appointments',  # Depends on patients
                'budgets',       # Depends on patients
                'clinical',      # Depends on patients
                'finances',      # Depends on patients and treatments
            ]
            
            # Check if reordering is needed
            current_order = [app for app, _, _ in current_migrations]
            needs_fix = False
            
            # Check for specific problematic orderings
            for app, _, _ in current_migrations:
                if app == 'finances':
                    # finances should come after patients and treatments
                    if 'patients' not in current_order[:current_order.index('finances')]:
                        needs_fix = True
                        break
                    if 'treatments' not in current_order[:current_order.index('finances')]:
                        needs_fix = True
                        break
                elif app == 'treatments':
                    # treatments should come after patients
                    if 'patients' not in current_order[:current_order.index('treatments')]:
                        needs_fix = True
                        break
                elif app in ['appointments', 'budgets', 'clinical']:
                    # These should come after patients
                    if 'patients' not in current_order[:current_order.index(app)]:
                        needs_fix = True
                        break
            
            if not needs_fix:
                self.stdout.write(self.style.SUCCESS(
                    'Migration order is correct. No fix needed.'
                ))
                return
            
            self.stdout.write(self.style.WARNING(
                '\nMigration order is INCORRECT and needs to be fixed.'
            ))
            
            if apply:
                self.stdout.write(self.style.WARNING('Fixing migration history...'))
                
                # Delete the problematic migration records
                cursor.execute("""
                    DELETE FROM django_migrations 
                    WHERE app IN %s AND name = '0001_initial';
                """, (tuple(affected_apps),))
                
                deleted_count = cursor.rowcount
                self.stdout.write(self.style.SUCCESS(
                    f'Deleted {deleted_count} migration records.'
                ))
                
                # Re-insert them in the correct order with staggered timestamps
                from datetime import datetime, timedelta
                base_time = datetime.now()
                
                for idx, app in enumerate(correct_order):
                    if app in current_order:
                        # Insert with incremental timestamp
                        timestamp = base_time + timedelta(seconds=idx)
                        cursor.execute("""
                            INSERT INTO django_migrations (app, name, applied)
                            VALUES (%s, %s, %s);
                        """, (app, '0001_initial', timestamp))
                        self.stdout.write(self.style.SUCCESS(
                            f'Re-inserted {app}.0001_initial at {timestamp}'
                        ))
                
                self.stdout.write(self.style.SUCCESS(
                    '\n✅ Migration history fixed successfully!'
                ))
                self.stdout.write(self.style.SUCCESS(
                    'You can now run `python manage.py migrate` to apply any pending migrations.'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    '\nTo apply the fix, run: python manage.py fix_migration_history --apply'
                ))
