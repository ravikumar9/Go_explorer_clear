"""Check DB connectivity, logs dir writeability and optionally collectstatic.
Usage: python manage.py check_dev
"""
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from pathlib import Path
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Run quick DEV checks: DB connection, logs dir, and collectstatic dry-run'

    def add_arguments(self, parser):
        parser.add_argument('--collectstatic', action='store_true', help='Run collectstatic --noinput')

    def handle(self, *args, **options):
        self.stdout.write('Checking database connection...')
        db_conn = connections['default']
        try:
            db_conn.ensure_connection()
            self.stdout.write(self.style.SUCCESS('✓ Database connection OK'))
        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f'✗ DB connection failed: {e}'))
            sys.exit(2)

        self.stdout.write('Checking logs directory...')
        logs_dir = Path(settings.BASE_DIR) / 'logs'
        try:
            logs_dir.mkdir(parents=True, exist_ok=True)
            test_file = logs_dir / 'check_dev_test.txt'
            test_file.write_text('ok')
            test_file.unlink()
            self.stdout.write(self.style.SUCCESS('✓ Logs directory writable'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Cannot write to logs dir: {e}'))

        if options['collectstatic']:
            self.stdout.write('Running collectstatic --noinput (this will copy static files)')
            from django.core.management import call_command
            try:
                call_command('collectstatic', '--noinput')
                self.stdout.write(self.style.SUCCESS('✓ collectstatic completed'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ collectstatic failed: {e}'))
                sys.exit(3)

        self.stdout.write(self.style.SUCCESS('\nAll DEV checks passed (or reported above).'))
