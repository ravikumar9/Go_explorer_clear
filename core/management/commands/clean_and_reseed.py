"""
Clean database and reseed from scratch
Usage: python manage.py clean_and_reseed
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from core.models import City
from bookings.models import Booking, BusBooking
from buses.models import BusRoute, BusSchedule, Bus, BusOperator, SeatLayout
from hotels.models import Hotel, RoomType, RoomAvailability, HotelDiscount
from packages.models import Package, PackageDeparture, PackageItinerary


class Command(BaseCommand):
    help = 'Clean database and reseed development data'

    def handle(self, *args, **options):
        self.stdout.write('=' * 60)
        self.stdout.write('DATABASE CLEANUP & RESEED')
        self.stdout.write('=' * 60)
        
        # Delete data in correct order to respect foreign keys
        self.stdout.write('\n[1/7] Deleting bookings...')
        BusBooking.objects.all().delete()
        Booking.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Bookings deleted'))
        
        self.stdout.write('\n[2/7] Deleting bus data...')
        SeatLayout.objects.all().delete()
        BusSchedule.objects.all().delete()
        BusRoute.objects.all().delete()
        Bus.objects.all().delete()
        BusOperator.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Bus data deleted'))
        
        self.stdout.write('\n[3/7] Deleting hotel data...')
        RoomAvailability.objects.all().delete()
        RoomType.objects.all().delete()
        HotelDiscount.objects.all().delete()
        Hotel.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Hotel data deleted'))
        
        self.stdout.write('\n[4/7] Deleting package data...')
        PackageDeparture.objects.all().delete()
        PackageItinerary.objects.all().delete()
        Package.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('✓ Package data deleted'))
        
        self.stdout.write('\n[5/7] Deleting cities...')
        count = City.objects.all().count()
        City.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'✓ {count} cities deleted'))
        
        self.stdout.write('\n[6/7] Running fresh seed...')
        call_command('seed_dev')
        
        self.stdout.write('\n[7/7] Cleanup complete!')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('✅ DATABASE CLEANED & RESEEDED'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
