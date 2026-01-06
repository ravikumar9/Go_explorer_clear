"""Seed development database with convenient command.
Usage: python manage.py seed_dev
This will run `seed_hotels` (existing command) and the `populate_bookings.py` script
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from pathlib import Path
import importlib.util
import sys

class Command(BaseCommand):
    help = 'Seed development database with sample data (hotels + bus bookings)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding hotels...')
        call_command('seed_hotels')

        self.stdout.write('Adding hotel images...')
        call_command('add_hotel_images')

        self.stdout.write('Seeding bus operators, buses and routes...')
        call_command('add_bus_operators')

        self.stdout.write('Adding packages...')
        call_command('add_packages')

        # Create dev admin user
        self.stdout.write('Ensuring development admin user exists...')
        call_command('create_dev_admin')

        # Locate populate_bookings.py at project root and call its main() function
        project_root = Path(__file__).resolve().parents[3]
        script_path = project_root / 'populate_bookings.py'

        if script_path.exists():
            self.stdout.write('Seeding bus bookings via populate_bookings.py...')
            spec = importlib.util.spec_from_file_location('populate_bookings', str(script_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'main'):
                module.main()
                self.stdout.write(self.style.SUCCESS('✓ Seed complete'))
            else:
                self.stdout.write(self.style.WARNING('populate_bookings.py has no main()'))
        else:
            self.stdout.write(self.style.WARNING(f'populate_bookings.py not found at {script_path}'))
