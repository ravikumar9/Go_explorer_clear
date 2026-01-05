import requests
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from buses.models import BusOperator, Bus, BusRoute, BusSchedule
from core.models import City
from datetime import datetime, time, timedelta
import random

class Command(BaseCommand):
    help = 'Add bus operators with details and images from the internet'

    def handle(self, *args, **options):
        # Bus operator data with image URLs from Pexels/Unsplash
        operators_data = [
            {
                'name': 'Shatabdi Express',
                'description': 'Premium long-distance bus service with modern amenities',
                'contact_phone': '+91-9876543210',
                'rating': 4.7,
                'image_url': 'https://images.unsplash.com/photo-1570710968482-c7a6b06a6c48?w=800'
            },
            {
                'name': 'Royal Travels',
                'description': 'Affordable and reliable bus operator across India',
                'contact_phone': '+91-9876543211',
                'rating': 4.5,
                'image_url': 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800'
            },
            {
                'name': 'Volvo Buses',
                'description': 'Luxury coach operator with premium seating and comfort',
                'contact_phone': '+91-9876543212',
                'rating': 4.8,
                'image_url': 'https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800'
            },
            {
                'name': 'Green Line Tours',
                'description': 'Eco-friendly bus service with excellent customer care',
                'contact_phone': '+91-9876543213',
                'rating': 4.4,
                'image_url': 'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=800'
            },
            {
                'name': 'Interstate Travels',
                'description': 'Connect major cities with comfortable overnight services',
                'contact_phone': '+91-9876543214',
                'rating': 4.6,
                'image_url': 'https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=800'
            }
        ]

        # Get or create cities
        cities_data = [
            ('Mumbai', 'Maharashtra'),
            ('Delhi', 'Delhi'),
            ('Bangalore', 'Karnataka'),
            ('Chennai', 'Tamil Nadu'),
            ('Hyderabad', 'Telangana'),
            ('Kolkata', 'West Bengal'),
            ('Pune', 'Maharashtra'),
            ('Goa', 'Goa'),
        ]

        cities = {}
        for city_name, state in cities_data:
            city, _ = City.objects.get_or_create(
                name=city_name,
                defaults={'state': state}
            )
            cities[city_name] = city

        # Create operators and buses
        for idx, op_data in enumerate(operators_data):
            operator, created = BusOperator.objects.get_or_create(
                name=op_data['name'],
                defaults={
                    'description': op_data['description'],
                    'contact_phone': op_data['contact_phone'],
                    'rating': op_data['rating'],
                }
            )

            if created:
                # Download and save image (try primary URL then fallback to local placeholder)
                def _download_first_success(urls):
                    for u in urls:
                        try:
                            resp = requests.get(u, timeout=5)
                            if resp.status_code == 200:
                                return resp.content
                        except Exception:
                            continue
                    return None

                local_placeholder = os.path.join(settings.BASE_DIR, 'static', 'images', 'bus_placeholder.svg')
                content = _download_first_success([op_data['image_url']])
                if not content:
                    try:
                        with open(local_placeholder, 'rb') as f:
                            content = f.read()
                            self.stdout.write(self.style.WARNING(f'⚠ Using local placeholder for {op_data["name"]}'))
                    except Exception:
                        content = None

                if content:
                    try:
                        file_content = ContentFile(content)
                        filename = f"{slugify(op_data['name'])}_logo.jpg"
                        operator.logo.save(filename, file_content, save=True)
                        self.stdout.write(f"✓ Added image for {op_data['name']}")
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"⚠ Could not save image for {op_data['name']}: {e}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠ No image available for {op_data['name']}"))

            # Create 2 buses per operator
            bus_types = ['Volvo', 'Scania', 'Tata']
            for bus_idx in range(2):
                bus_number = f"{op_data['name'][:3].upper()}{1000 + idx * 10 + bus_idx}"
                bus, created = Bus.objects.get_or_create(
                    bus_number=bus_number,
                    operator=operator,
                    defaults={
                        'bus_name': f"{op_data['name']} {bus_types[bus_idx % 3]}",
                        'bus_type': 'AC_NON_SLEEPER' if bus_idx == 0 else 'AC_SLEEPER',
                        'total_seats': 48,
                        'has_ac': True,
                        'has_wifi': random.choice([True, False]),
                        'has_charging_point': True,
                        'has_blanket': bus_idx != 0,
                        'has_water_bottle': True,
                        'has_tv': random.choice([True, False]),
                    }
                )

                if created:
                    # Create routes for the bus
                    city_pairs = [
                        ('Mumbai', 'Bangalore'),
                        ('Delhi', 'Jaipur'),
                        ('Bangalore', 'Chennai'),
                        ('Pune', 'Goa'),
                    ]

                    for source_name, dest_name in city_pairs[:2]:
                        if source_name in cities and dest_name in cities:
                            route, _ = BusRoute.objects.get_or_create(
                                bus=bus,
                                source_city=cities[source_name],
                                destination_city=cities[dest_name],
                                defaults={
                                    'departure_time': time(20, 0),
                                    'arrival_time': time(8, 0),
                                    'duration_hours': 12.0,
                                    'distance_km': random.randint(400, 800),
                                    'base_fare': random.randint(800, 2000),
                                }
                            )

                            if _ is True:  # newly created
                                # Create schedules for the route
                                for day_offset in range(7):
                                    schedule_date = datetime.now().date() + timedelta(days=day_offset + 1)
                                    BusSchedule.objects.get_or_create(
                                        route=route,
                                        date=schedule_date,
                                        defaults={
                                            'available_seats': bus.total_seats,
                                            'fare': float(route.base_fare),
                                            'is_active': True,
                                        }
                                    )

            self.stdout.write(self.style.SUCCESS(
                f'✓ Created operator: {op_data["name"]} with buses and routes'
            ))

        self.stdout.write(self.style.SUCCESS('Successfully added all bus operators with images'))
