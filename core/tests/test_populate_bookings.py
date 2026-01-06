from django.test import TestCase
import importlib.util
from pathlib import Path


class PopulateBookingsModuleTest(TestCase):
    def test_main_does_not_call_django_setup_when_apps_ready(self):
        """Loading and running the project-root populate_bookings.main() must not raise
        even when Django is already initialized (e.g., when called from seed_dev).
        """
        project_root = Path(__file__).resolve().parents[2]
        script_path = project_root / 'populate_bookings.py'
        spec = importlib.util.spec_from_file_location('populate_bookings', str(script_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # Should not raise an exception even though Django is configured for tests
        module.main()
