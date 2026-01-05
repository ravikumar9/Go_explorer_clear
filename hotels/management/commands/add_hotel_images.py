"""
Management command to add images to hotels
"""
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import requests
import os
from django.conf import settings
from hotels.models import Hotel, HotelImage


class Command(BaseCommand):
    help = 'Add images to hotels from internet'

    HOTEL_IMAGES = {
        'Taj Mahal Palace': [
            'https://images.unsplash.com/photo-1511919612990-1de1f99d5f2b?w=1200&h=800&fit=crop',
            'https://images.unsplash.com/photo-1501117716987-c8e8f1f8b6f4?w=1200&h=800&fit=crop',
        ],
        'The Leela Palace Delhi': [
            'https://images.unsplash.com/photo-1528909514045-2fa4ac7a08ba?w=1200&h=800&fit=crop',
            'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=1200&h=800&fit=crop',
        ],
        'Taj Connemara Chennai': [
            'https://images.unsplash.com/photo-1526772662000-3f88f10405ff?w=1200&h=800&fit=crop',
            'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=1200&h=800&fit=crop',
        ],
        'Taj Rambagh Palace Jaipur': [
            'https://images.unsplash.com/photo-1508057198894-247b23fe5ade?w=1200&h=800&fit=crop',
            'https://images.unsplash.com/photo-1504328341455-331f6f2b31a8?w=1200&h=800&fit=crop',
        ],
        'Tajview Agra': [
            'https://images.unsplash.com/photo-1491557345352-5929e343eb89?w=1200&h=800&fit=crop',
            'https://images.unsplash.com/photo-1505765054867-0be56c3c7b41?w=1200&h=800&fit=crop',
        ],
        'Taj Bengal Kolkata': [
            'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=1200&h=800&fit=crop',
            'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=1200&h=800&fit=crop',
        ],
        # Legacy entries (kept for backwards compatibility)
        'Bangalore Tech Suites': [
            'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1571896349842-b58d8ceb4ee0?w=800&h=600&fit=crop',
        ],
        'Mumbai Luxury': [
            'https://images.unsplash.com/photo-1594822303529-c80c806667a3?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&h=600&fit=crop',
        ],
    }

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to add hotel images...'))

        for hotel_name, image_urls in self.HOTEL_IMAGES.items():
            try:
                hotel = Hotel.objects.get(name=hotel_name)
                
                def _download_first_success(urls):
                    for u in urls:
                        try:
                            resp = requests.get(u, timeout=5)
                            if resp.status_code == 200:
                                return resp.content
                        except Exception:
                            continue
                    return None

                # Paths to local fallback placeholders
                local_placeholder = os.path.join(settings.BASE_DIR, 'static', 'images', 'hotel_placeholder.svg')

                # Add first image as main image if not already set
                if not hotel.image:
                    self.stdout.write(f'Adding main image to {hotel_name}...')
                    content = _download_first_success(image_urls)
                    if not content:
                        # Try using local placeholder
                        try:
                            with open(local_placeholder, 'rb') as f:
                                content = f.read()
                                self.stdout.write(self.style.WARNING(f'⚠ Using local placeholder for {hotel_name}'))
                        except Exception:
                            content = None
                    if content:
                        try:
                            image_name = f'{hotel_name.lower().replace(" ", "_")}_main.jpg'
                            hotel.image.save(
                                image_name,
                                ContentFile(content),
                                save=True
                            )
                            self.stdout.write(self.style.SUCCESS(f'✓ Added main image to {hotel_name}'))
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'⚠ Failed to save image for {hotel_name}: {str(e)}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'⚠ No image available for {hotel_name}'))

                # Add additional images to gallery
                for idx, image_url in enumerate(image_urls[1:], start=1):
                    try:
                        if not HotelImage.objects.filter(hotel=hotel, caption__icontains=f'Gallery {idx}').exists():
                            content = _download_first_success([image_url])
                            if not content:
                                try:
                                    with open(local_placeholder, 'rb') as f:
                                        content = f.read()
                                except Exception:
                                    content = None

                            if content:
                                image_name = f'{hotel_name.lower().replace(" ", "_")}_gallery_{idx}.jpg'
                                HotelImage.objects.create(
                                    hotel=hotel,
                                    caption=f'Gallery {idx}',
                                    image=ContentFile(content, name=image_name),
                                    is_primary=(idx == 1)
                                )
                                self.stdout.write(self.style.SUCCESS(f'✓ Added gallery image {idx} to {hotel_name}'))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f'⚠ Failed to download gallery image for {hotel_name}: {str(e)}'))
                
            except Hotel.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'⚠ Hotel "{hotel_name}" not found'))

        self.stdout.write(self.style.SUCCESS('✓ Finished adding hotel images!'))
