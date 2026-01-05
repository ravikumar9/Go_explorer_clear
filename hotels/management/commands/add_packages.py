import requests
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from packages.models import Package, PackageDeparture, PackageItinerary
from core.models import City
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Add tour packages with images from the internet'

    def handle(self, *args, **options):
        # Package data with images
        packages_data = [
            {
                'name': 'Bali Paradise Package',
                'destination': 'Bali',
                'duration_days': 5,
                'duration_nights': 4,
                'package_type': 'beach',
                'starting_price': 45000,
                'description': 'Enjoy pristine beaches, temples, and tropical landscapes in beautiful Bali.',
                'image_url': 'https://images.unsplash.com/photo-1537225228614-b19fdf4e78c5?w=800',
                'inclusions': {
                    'hotel': True,
                    'transport': True,
                    'meals': True,
                    'sightseeing': True,
                }
            },
            {
                'name': 'Himalayan Trek Adventure',
                'destination': 'Himalayas',
                'duration_days': 7,
                'duration_nights': 6,
                'package_type': 'adventure',
                'starting_price': 38000,
                'description': 'Challenge yourself with trekking through the majestic Himalayan mountains.',
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
                'inclusions': {
                    'hotel': True,
                    'transport': True,
                    'meals': True,
                    'sightseeing': True,
                }
            },
            {
                'name': 'Dubai Luxury Escape',
                'destination': 'Dubai',
                'duration_days': 4,
                'duration_nights': 3,
                'package_type': 'luxury',
                'starting_price': 55000,
                'description': 'Experience the glamour and luxury of modern Dubai with world-class amenities.',
                'image_url': 'https://images.unsplash.com/photo-1512453909613-34fccebf17a6?w=800',
                'inclusions': {
                    'hotel': True,
                    'transport': True,
                    'meals': True,
                    'sightseeing': True,
                }
            },
            {
                'name': 'Kerala Backwaters Cruise',
                'destination': 'Kerala',
                'duration_days': 5,
                'duration_nights': 4,
                'package_type': 'beach',
                'starting_price': 32000,
                'description': 'Relax on a houseboat cruise through scenic Kerala backwaters and spice plantations.',
                'image_url': 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=800',
                'inclusions': {
                    'hotel': True,
                    'transport': True,
                    'meals': True,
                    'sightseeing': True,
                }
            },
            {
                'name': 'Egypt Historical Tour',
                'destination': 'Egypt',
                'duration_days': 8,
                'duration_nights': 7,
                'package_type': 'cultural',
                'starting_price': 65000,
                'description': 'Explore ancient pyramids, temples, and the magnificent Nile River.',
                'image_url': 'https://images.unsplash.com/photo-1570710968482-c7a6b06a6c48?w=800',
                'inclusions': {
                    'hotel': True,
                    'transport': True,
                    'meals': True,
                    'sightseeing': True,
                }
            },
            {
                'name': 'Thailand Beach Retreat',
                'destination': 'Thailand',
                'duration_days': 6,
                'duration_nights': 5,
                'package_type': 'beach',
                'starting_price': 42000,
                'description': 'Island hop through Thailand with pristine beaches, temples, and local culture.',
                'image_url': 'https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=800',
                'inclusions': {
                    'hotel': True,
                    'transport': True,
                    'meals': False,
                    'sightseeing': True,
                }
            },
            {
                'name': 'Swiss Alps Package',
                'destination': 'Switzerland',
                'duration_days': 7,
                'duration_nights': 6,
                'package_type': 'adventure',
                'starting_price': 75000,
                'description': 'Experience alpine beauty, charming villages, and world-class skiing in the Swiss Alps.',
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
                'inclusions': {
                    'hotel': True,
                    'transport': True,
                    'meals': True,
                    'sightseeing': True,
                }
            },
            {
                'name': 'Northern Lights Adventure',
                'destination': 'Iceland',
                'duration_days': 5,
                'duration_nights': 4,
                'package_type': 'adventure',
                'starting_price': 85000,
                'description': 'Chase the magical Northern Lights in Iceland with stunning natural landscapes.',
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800',
                'inclusions': {
                    'hotel': True,
                    'transport': True,
                    'meals': True,
                    'sightseeing': True,
                }
            }
        ]

        # Get or create default city
        city, _ = City.objects.get_or_create(
            name='India',
            defaults={'state': 'Multiple'}
        )

        # Create packages
        for pkg_data in packages_data:
            package, created = Package.objects.get_or_create(
                name=pkg_data['name'],
                defaults={
                    'description': pkg_data['description'],
                    'package_type': pkg_data['package_type'],
                    'duration_days': pkg_data['duration_days'],
                    'duration_nights': pkg_data['duration_nights'],
                    'starting_price': pkg_data['starting_price'],
                    'includes_hotel': pkg_data['inclusions']['hotel'],
                    'includes_transport': pkg_data['inclusions']['transport'],
                    'includes_meals': pkg_data['inclusions']['meals'],
                    'includes_sightseeing': pkg_data['inclusions']['sightseeing'],
                    'is_active': True,
                    'rating': round(random.uniform(3.5, 5.0), 1),
                }
            )

            if created:
                # Add destination city
                package.destination_cities.add(city)
                
                # Download and save image with fallback to local placeholder
                def _download_first_success(urls):
                    for u in urls:
                        try:
                            resp = requests.get(u, timeout=5)
                            if resp.status_code == 200:
                                return resp.content
                        except Exception:
                            continue
                    return None

                local_placeholder = os.path.join(settings.BASE_DIR, 'static', 'images', 'package_placeholder.svg')
                content = _download_first_success([pkg_data['image_url']])
                if not content:
                    try:
                        with open(local_placeholder, 'rb') as f:
                            content = f.read()
                            self.stdout.write(self.style.WARNING(f'⚠ Using local placeholder for {pkg_data["name"]}'))
                    except Exception:
                        content = None

                if content:
                    try:
                        file_content = ContentFile(content)
                        filename = f"{slugify(pkg_data['name'])}.jpg"
                        package.image.save(filename, file_content, save=True)
                        self.stdout.write(f"✓ Added image for {pkg_data['name']}")
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"⚠ Could not save image for {pkg_data['name']}: {e}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠ No image available for {pkg_data['name']}"))

                # Create sample itinerary
                for day in range(1, pkg_data['duration_days'] + 1):
                    PackageItinerary.objects.get_or_create(
                        package=package,
                        day_number=day,
                        defaults={
                            'title': f"Day {day} - Exploration",
                            'description': f"Experience the beauty and culture of {pkg_data['destination']}",
                            'activities': 'Sightseeing, Photography, Local cuisine',
                            'meals_included': 'Breakfast, Dinner' if pkg_data['inclusions']['meals'] else 'None',
                            'accommodation': 'Hotel' if pkg_data['inclusions']['hotel'] else 'None',
                        }
                    )

                # Create departures for the next 30 days
                today = datetime.now().date()
                for day_offset in range(0, 30, 7):  # Weekly departures
                    departure_date = today + timedelta(days=day_offset + 1)
                    return_date = departure_date + timedelta(days=pkg_data['duration_days'])
                    PackageDeparture.objects.get_or_create(
                        package=package,
                        departure_date=departure_date,
                        defaults={
                            'return_date': return_date,
                            'available_slots': random.randint(10, 30),
                            'price_per_person': pkg_data['starting_price'],
                            'is_active': True,
                        }
                    )

                self.stdout.write(self.style.SUCCESS(
                    f'✓ Created package: {pkg_data["name"]} with departures'
                ))

        self.stdout.write(self.style.SUCCESS('Successfully added all tour packages with images'))
