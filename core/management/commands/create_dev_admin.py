from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create development admin user with well-known credentials (no-op if exists)'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='goexplorer_dev_admin')
        parser.add_argument('--password', default='Thepowerof@9')
        parser.add_argument('--email', default='dev-admin@goexplorer.dev')

    def handle(self, *args, **options):
        User = get_user_model()
        username = options['username']
        password = options['password']
        email = options['email']

        user = User.objects.filter(username=username).first()
        if user:
            self.stdout.write(self.style.WARNING(f'Admin user "{username}" already exists'))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'✓ Created admin user: {username}'))
