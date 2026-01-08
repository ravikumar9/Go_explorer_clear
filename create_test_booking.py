#!/usr/bin/env python
"""
Test script to create a test booking for confirmation page verification
Usage: python manage.py shell < create_test_booking.py
"""

import os
import django
from django.contrib.auth import get_user_model
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goexplorer.settings')
django.setup()

from bookings.models import Booking
from buses.models import Bus, BusSchedule, SeatLayout
from buses.models import BoardingPoint, DroppingPoint

User = get_user_model()

# Get admin user
admin = User.objects.get(email='admin@example.com')

# Get bus, route, schedule
bus = Bus.objects.get(id=1)
schedule = BusSchedule.objects.filter(bus=bus).first()

# Get boarding/dropping points
boarding = BoardingPoint.objects.filter(route=schedule.route).first()
dropping = DroppingPoint.objects.filter(route=schedule.route).first()

# Create test booking
booking = Booking.objects.create(
    user=admin,
    booking_type='bus',
    total_amount=Decimal('3075.00'),  # 1500 (fare) * 2 (seats) + 2% + 5% GST
    customer_name='Test Customer',
    customer_email='test@example.com',
    customer_phone='9876543210',
    status='confirmed',
    source_city=schedule.route.source_city,
    destination_city=schedule.route.destination_city,
)

print(f"TEST BOOKING CREATED:")
print(f"  Booking ID: {booking.booking_id}")
print(f"  Customer: {booking.customer_name}")
print(f"  Email: {booking.customer_email}")
print(f"  Phone: {booking.customer_phone}")
print(f"  Total: Rs {booking.total_amount}")
print(f"  URL: http://localhost:8000/bookings/{booking.booking_id}/")
print(f"\nOpen this URL in browser to see confirmation page with real data")
