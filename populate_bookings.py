#!/usr/bin/env python
"""
Script to populate sample booking data for testing enhanced booking admin panel
"""
import os
import django
from datetime import date, timedelta
from decimal import Decimal

def main():
    # Note: Do NOT call django.setup() here. This function is called either:
    # 1. From seed_dev management command (Django already initialized)
    # 2. From __main__ (see bottom of file) - which handles setup
    
    from django.contrib.auth import get_user_model
    from bookings.models import Booking, BusBooking, BusBookingSeat
    from buses.models import BusSchedule, BusOperator, Bus, BusRoute, SeatLayout
    from core.models import City

    User = get_user_model()

    # Create test users if not exist
    admin = User.objects.filter(username='admin').first()
    if not admin:
        admin = User.objects.create_superuser('admin', 'admin@example.com', 'AdminPassw0rd!')

    customers = []
    for i in range(5):
        customer, _ = User.objects.get_or_create(
            username=f'customer{i}',
            defaults={
                'email': f'customer{i}@example.com',
                'first_name': f'Customer {i}',
                'last_name': f'User {i}'
            }
        )
        customers.append(customer)
        if not customer.has_usable_password():
            customer.set_password('Pass@1234')
            customer.save()

    # Get or create cities
    bangalore = City.objects.filter(code='BLR').first()
    delhi = City.objects.filter(code='DEL').first()
    mumbai = City.objects.filter(code='MUM').first()

    if not bangalore:
        bangalore = City.objects.create(name='Bangalore', state='Karnataka', code='BLR', is_popular=True)
    if not delhi:
        delhi = City.objects.create(name='Delhi', state='Delhi', code='DEL', is_popular=True)
    if not mumbai:
        mumbai = City.objects.create(name='Mumbai', state='Maharashtra', code='MUM', is_popular=True)

    # Get or create bus operator and bus
    bus_partner = User.objects.filter(username='bus_partner').first()
    if bus_partner:
        bus_op = BusOperator.objects.filter(user=bus_partner).first() or BusOperator.objects.filter(name='GoExplorer Express').first()
        if not bus_op:
            bus_op = BusOperator.objects.create(
                name='GoExplorer Express',
                contact_phone='9999999999',
                contact_email='busops@goexplorer.com',
                user=bus_partner,
                is_active=True
            )
    else:
        bus_op = BusOperator.objects.filter(name='GoExplorer Express').first()
        if not bus_op:
            bus_op = BusOperator.objects.create(
                name='GoExplorer Express',
                contact_phone='9999999999',
                contact_email='busops@goexplorer.com',
                is_active=True
            )

    bus, _ = Bus.objects.get_or_create(
        bus_number='KA01AB2024',
        defaults={
            'operator': bus_op,
            'bus_name': 'GoExpress Premium',
            'bus_type': 'ac_sleeper',
            'total_seats': 40,
            'has_ac': True,
            'has_wifi': True,
            'has_charging_point': True,
            'average_rating': Decimal('4.5'),
            'is_active': True
        }
    )

    # Create routes
    route, _ = BusRoute.objects.get_or_create(
        bus=bus,
        source_city=bangalore,
        destination_city=delhi,
        route_name='BLR-DEL Express',
        defaults={
            'departure_time': '08:00',
            'arrival_time': '18:00',
            'duration_hours': Decimal('10.00'),
            'distance_km': Decimal('250.00'),
            'base_fare': Decimal('1500.00')
        }
    )

    # Create schedules for various dates
    base_date = date.today() + timedelta(days=7)
    for i in range(10):
        sched_date = base_date + timedelta(days=i)
        schedule, _ = BusSchedule.objects.get_or_create(
            route=route,
            date=sched_date,
            defaults={
                'available_seats': 40,
                'booked_seats': 0,
                'fare': Decimal('1500.00'),
                'is_active': True,
                'is_cancelled': False
            }
        )

    # Create seat layouts
    for seat_num in range(1, 41):
        row = (seat_num - 1) // 4 + 1
        col = (seat_num - 1) % 4 + 1
        reserved = 'ladies' if seat_num % 5 == 0 else 'general'
        
        SeatLayout.objects.get_or_create(
            bus=bus,
            seat_number=f'{seat_num}',
            defaults={
                'seat_type': 'sleeper_lower' if seat_num <= 20 else 'sleeper_upper',
                'row': row,
                'column': col,
                'deck': 1 if seat_num <= 20 else 2,
                'reserved_for': reserved
            }
        )

    print("✓ Sample data created successfully!")
    print("\nBooking Test Scenarios:")
    print("=" * 60)

    # Create sample bookings with different statuses
    schedule = BusSchedule.objects.filter(route=route, date__gte=base_date).first()

    # Pending booking
    pending_booking = Booking.objects.create(
        user=customers[0],
        booking_type='bus',
        status='pending',
        total_amount=Decimal('3000.00'),
        paid_amount=Decimal('0.00'),
        customer_name='Raj Kumar',
        customer_email='raj@example.com',
        customer_phone='9876543210',
        special_requests='Window seat preferred'
    )
    BusBooking.objects.create(
        booking=pending_booking,
        bus_schedule=schedule,
        bus_route=route,
        journey_date=schedule.date,
        boarding_point='Majestic Bus Stand, Bangalore',
        dropping_point='ISBT, Delhi'
    )
    print(f"1. ✓ Pending Booking Created: {pending_booking.booking_id}")
    print(f"   Customer: {pending_booking.customer_name}")
    print(f"   Status: PENDING | Amount: ₹{pending_booking.total_amount}")

    # Confirmed booking
    confirmed_booking = Booking.objects.create(
        user=customers[1],
        booking_type='bus',
        status='confirmed',
        total_amount=Decimal('3000.00'),
        paid_amount=Decimal('3000.00'),
        customer_name='Priya Singh',
        customer_email='priya@example.com',
        customer_phone='9876543211'
    )
    bus_booking = BusBooking.objects.create(
        booking=confirmed_booking,
        bus_schedule=schedule,
        bus_route=route,
        journey_date=schedule.date,
        boarding_point='Electronic City, Bangalore',
        dropping_point='Kasol, Delhi'
    )

    # Add seats to confirmed booking
    seat1 = SeatLayout.objects.filter(bus=bus, seat_number='5').first()
    seat2 = SeatLayout.objects.filter(bus=bus, seat_number='6').first()
    if seat1:
        BusBookingSeat.objects.get_or_create(
            bus_booking=bus_booking,
            seat=seat1,
            defaults={
                'passenger_name': 'Priya Singh',
                'passenger_age': 28,
                'passenger_gender': 'F'
            }
        )
    if seat2:
        BusBookingSeat.objects.get_or_create(
            bus_booking=bus_booking,
            seat=seat2,
            defaults={
                'passenger_name': 'Aman Singh',
                'passenger_age': 30,
                'passenger_gender': 'M'
            }
        )
    print(f"\n2. ✓ Confirmed Booking Created: {confirmed_booking.booking_id}")
    print(f"   Customer: {confirmed_booking.customer_name}")
    print(f"   Status: CONFIRMED | Amount: ₹{confirmed_booking.total_amount}")
    print(f"   Seats Booked: 2 (Seat 5, 6) | Ladies Reserved Respected")

    # Cancelled booking
    cancelled_booking = Booking.objects.create(
        user=customers[2],
        booking_type='bus',
        status='cancelled',
        total_amount=Decimal('1500.00'),
        paid_amount=Decimal('1500.00'),
        customer_name='Vikram Patel',
        customer_email='vikram@example.com',
        customer_phone='9876543212',
        cancellation_reason='Emergency travel plans changed',
        refund_amount=Decimal('1500.00')
    )
    BusBooking.objects.create(
        booking=cancelled_booking,
        bus_schedule=schedule,
        bus_route=route,
        journey_date=schedule.date,
        boarding_point='Brigade Road, Bangalore',
        dropping_point='Indira Gandhi Airport, Delhi'
    )
    print(f"\n3. ✓ Cancelled Booking Created: {cancelled_booking.booking_id}")
    print(f"   Customer: {cancelled_booking.customer_name}")
    print(f"   Status: CANCELLED | Refund: ₹{cancelled_booking.refund_amount}")

    # Completed booking
    completed_booking = Booking.objects.create(
        user=customers[3],
        booking_type='bus',
        status='completed',
        total_amount=Decimal('2250.00'),
        paid_amount=Decimal('2250.00'),
        customer_name='Neha Desai',
        customer_email='neha@example.com',
        customer_phone='9876543213'
    )
    BusBooking.objects.create(
        booking=completed_booking,
        bus_schedule=schedule,
        bus_route=route,
        journey_date=schedule.date - timedelta(days=1),  # Past date
        boarding_point='Ulsoor Lake, Bangalore',
        dropping_point='Old Delhi Station'
    )
    print(f"\n4. ✓ Completed Booking Created: {completed_booking.booking_id}")
    print(f"   Customer: {completed_booking.customer_name}")
    print(f"   Status: COMPLETED | Trip Finished")

    # Soft-deleted booking
    deleted_booking = Booking.objects.create(
        user=customers[4],
        booking_type='bus',
        status='deleted',
        total_amount=Decimal('1500.00'),
        paid_amount=Decimal('0.00'),
        customer_name='Anil Kumar',
        customer_email='anil@example.com',
        customer_phone='9876543214',
        is_deleted=True,
        deleted_reason='Duplicate booking - user made error'
    )
    BusBooking.objects.create(
        booking=deleted_booking,
        bus_schedule=schedule,
        bus_route=route,
        journey_date=schedule.date + timedelta(days=3),
        boarding_point='Koramangala, Bangalore',
        dropping_point='New Delhi Railway Station'
    )
    print(f"\n5. ✓ Soft-Deleted Booking Created: {deleted_booking.booking_id}")
    print(f"   Customer: {deleted_booking.customer_name}")
    print(f"   Status: DELETED | Reason: {deleted_booking.deleted_reason}")

    print("\n" + "=" * 60)
    print("✅ All Test Scenarios Created Successfully!")
    print("\nAdmin Credentials:")
    print(f"  Username: admin")
    print(f"  Password: AdminPassw0rd!")
    print("\nTest Customer Accounts:")
    for i, cust in enumerate(customers):
        print(f"  customer{i} / Pass@1234")
    print("\n📊 Dashboard: http://localhost:8000/dashboard/")
    print("🔧 Admin Panel: http://localhost:8000/admin/")
    print("\n💡 Test Cases to Verify:")
    print("  1. Pending Booking - Can edit, confirm, or cancel")
    print("  2. Confirmed Booking - View seat details and passenger info")
    print("  3. Cancelled Booking - Shows refund details")
    print("  4. Completed Booking - Read-only (no edits allowed)")
    print("  5. Soft-Deleted Booking - Hidden from default list, visible in admin")
    print("\n🎯 Key Features to Test:")
    print("  • Edit boarding/dropping points")
    print("  • Change journey dates")
    print("  • Modify seat assignments")
    print("  • View audit logs of all changes")
    print("  • Soft delete with reason tracking")
    print("  • Pagination and search by booking ID/phone")
    print("  • Status badges with color coding")


if __name__ == '__main__':
    # Only set up Django when running as standalone script (not from manage.py or seed_dev)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goexplorer.settings')
    import django
    django.setup()
    main()
