"""
Management command to seed hotel database with sample data
Usage: python manage.py seed_hotels
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date, timedelta, datetime
from decimal import Decimal
import random

from hotels.models import Hotel, RoomType, RoomAvailability, HotelDiscount
from core.models import City


class Command(BaseCommand):
    help = 'Seed database with sample hotel data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing hotel data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing hotel data...'))
            Hotel.objects.all().delete()
            RoomType.objects.all().delete()
            RoomAvailability.objects.all().delete()
            HotelDiscount.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Data cleared'))

        # Create cities (expanded list of well-known tourism destinations)
        cities_data = [
            {'name': 'Mumbai', 'state': 'Maharashtra', 'country': 'India', 'code': 'MUM', 'is_popular': True},
            {'name': 'Delhi', 'state': 'Delhi', 'country': 'India', 'code': 'DEL', 'is_popular': True},
            {'name': 'Bangalore', 'state': 'Karnataka', 'country': 'India', 'code': 'BLR', 'is_popular': True},
            {'name': 'Hyderabad', 'state': 'Telangana', 'country': 'India', 'code': 'HYD', 'is_popular': True},
            {'name': 'Goa', 'state': 'Goa', 'country': 'India', 'code': 'GOA', 'is_popular': True},
            {'name': 'Chennai', 'state': 'Tamil Nadu', 'country': 'India', 'code': 'MAA', 'is_popular': True},
            {'name': 'Jaipur', 'state': 'Rajasthan', 'country': 'India', 'code': 'JAI', 'is_popular': True},
            {'name': 'Agra', 'state': 'Uttar Pradesh', 'country': 'India', 'code': 'AGR', 'is_popular': True},
            {'name': 'Udaipur', 'state': 'Rajasthan', 'country': 'India', 'code': 'UDR', 'is_popular': True},
            {'name': 'Kolkata', 'state': 'West Bengal', 'country': 'India', 'code': 'CCU', 'is_popular': True},
            {'name': 'Kochi', 'state': 'Kerala', 'country': 'India', 'code': 'COK', 'is_popular': True},
            {'name': 'Mysore', 'state': 'Karnataka', 'country': 'India', 'code': 'MYQ', 'is_popular': True},
            {'name': 'Varanasi', 'state': 'Uttar Pradesh', 'country': 'India', 'code': 'VNS', 'is_popular': True},
            {'name': 'Ahmedabad', 'state': 'Gujarat', 'country': 'India', 'code': 'AMD', 'is_popular': True},
            {'name': 'Pune', 'state': 'Maharashtra', 'country': 'India', 'code': 'PNQ', 'is_popular': True},
            {'name': 'Chandigarh', 'state': 'Chandigarh', 'country': 'India', 'code': 'IXC', 'is_popular': True},
            {'name': 'Pondicherry', 'state': 'Puducherry', 'country': 'India', 'code': 'PNY', 'is_popular': True},
            {'name': 'Leh', 'state': 'Ladakh', 'country': 'India', 'code': 'IXL', 'is_popular': True},
            {'name': 'Darjeeling', 'state': 'West Bengal', 'country': 'India', 'code': 'DRG', 'is_popular': True},
            {'name': 'Shimla', 'state': 'Himachal Pradesh', 'country': 'India', 'code': 'SHL', 'is_popular': True},
            {'name': 'Ooty', 'state': 'Tamil Nadu', 'country': 'India', 'code': 'OOT', 'is_popular': True},
            {'name': 'Manali', 'state': 'Himachal Pradesh', 'country': 'India', 'code': 'MNL', 'is_popular': True},
        ]
        
        cities = {}
        for city_data in cities_data:
            city, created = City.objects.get_or_create(
                code=city_data['code'],
                defaults={
                    'name': city_data['name'],
                    'state': city_data['state'],
                    'country': city_data['country'],
                    'is_popular': city_data.get('is_popular', False),
                }
            )
            cities[city_data['name']] = city
            if created:
                self.stdout.write(f'✓ Created city: {city.name}')

        # Hotel templates
        hotels_data = [
            {
                'name': 'Taj Mahal Palace',
                'city': 'Mumbai',
                'star_rating': 5,
                'review_rating': 4.8,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': True},
                'latitude': 18.9520,
                'longitude': 72.8347,
                'address': 'Apollo Bunder, Colaba, Mumbai',
                'contact_phone': '+91-22-6665-3366',
                'contact_email': 'reservations@tajhotel.com',
            },
            {
                'name': 'The Oberoi Mumbai',
                'city': 'Mumbai',
                'star_rating': 5,
                'review_rating': 4.7,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': True},
                'latitude': 18.9677,
                'longitude': 72.8252,
                'address': 'Nariman Point, Mumbai',
                'contact_phone': '+91-22-6632-5757',
                'contact_email': 'reservations@oberoihotels.com',
            },
            {
                'name': 'ITC Grand Central Mumbai',
                'city': 'Mumbai',
                'star_rating': 5,
                'review_rating': 4.6,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': False},
                'latitude': 18.9709,
                'longitude': 72.8206,
                'address': 'Dr Ambedkar Road, Girgaum, Mumbai',
                'contact_phone': '+91-22-4141-4141',
                'contact_email': 'reservations.grandcentral@itchotels.com',
            },
            {
                'name': 'The Leela Palace Delhi',
                'city': 'Delhi',
                'star_rating': 5,
                'review_rating': 4.8,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': True},
                'latitude': 28.5244,
                'longitude': 77.1855,
                'address': 'Diplomatic Enclave, New Delhi',
                'contact_phone': '+91-11-4101-1234',
                'contact_email': 'reservations.delhi@theleela.com',
            },
            {
                'name': 'The Oberoi Delhi',
                'city': 'Delhi',
                'star_rating': 4,
                'review_rating': 4.5,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': False},
                'latitude': 28.5976,
                'longitude': 77.2266,
                'address': 'Dr Zakir Hussain Marg, New Delhi',
                'contact_phone': '+91-11-4119-1919',
                'contact_email': 'reservations@oberoindia.com',
            },
            {
                'name': 'The Leela Palace Bangalore',
                'city': 'Bangalore',
                'star_rating': 5,
                'review_rating': 4.7,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': True},
                'latitude': 13.0268,
                'longitude': 77.5619,
                'address': 'Koramangala, Bangalore',
                'contact_phone': '+91-80-6127-1000',
                'contact_email': 'reservations.blr@theleela.com',
            },
            {
                'name': 'Taj Vivanta Bangalore',
                'city': 'Bangalore',
                'star_rating': 4,
                'review_rating': 4.4,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': False},
                'latitude': 13.0369,
                'longitude': 77.6021,
                'address': 'White Field, Bangalore',
                'contact_phone': '+91-80-6693-1234',
                'contact_email': 'reservations@tajhotels.com',
            },
            {
                'name': 'Park Hyatt Hyderabad',
                'city': 'Hyderabad',
                'star_rating': 5,
                'review_rating': 4.6,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': True},
                'latitude': 17.3850,
                'longitude': 78.4867,
                'address': 'Mindspace, Hyderabad',
                'contact_phone': '+91-40-6627-1234',
                'contact_email': 'reservations.hyderabad@hyatt.com',
            },
            {
                'name': 'The Oberoi Goa',
                'city': 'Goa',
                'star_rating': 5,
                'review_rating': 4.7,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': True},
                'latitude': 15.3395,
                'longitude': 73.8312,
                'address': 'Bogmalo Beach, Goa',
                'contact_phone': '+91-832-618-0000',
                'contact_email': 'reservations.goa@oberoihotels.com',
            },
            {
                'name': 'Taj Exotica Goa',
                'city': 'Goa',
                'star_rating': 5,
                'review_rating': 4.8,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': True},
                'latitude': 15.3789,
                'longitude': 73.8342,
                'address': 'South Goa, Goa',
                'contact_phone': '+91-832-266-8888',
                'contact_email': 'reservations@tajhotels.com',
            },
            # Additional famous-city hotels
            {
                'name': 'Taj Connemara Chennai',
                'city': 'Chennai',
                'star_rating': 5,
                'review_rating': 4.6,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': False},
                'latitude': 13.0674,
                'longitude': 80.2376,
                'address': 'Anna Salai, Chennai',
                'contact_phone': '+91-44-2817-1234',
                'contact_email': 'reservations.chennai@tajhotels.com',
            },
            {
                'name': 'Taj Rambagh Palace Jaipur',
                'city': 'Jaipur',
                'star_rating': 5,
                'review_rating': 4.7,
                'amenities': {'wifi': True, 'parking': True, 'pool': False, 'gym': False, 'restaurant': True, 'spa': False},
                'latitude': 26.9190,
                'longitude': 75.8160,
                'address': 'Ram Niwas Bagh, Jaipur',
                'contact_phone': '+91-141-222-1234',
                'contact_email': 'reservations.jaipur@tajhotels.com',
            },
            {
                'name': 'Tajview Agra',
                'city': 'Agra',
                'star_rating': 4,
                'review_rating': 4.4,
                'amenities': {'wifi': True, 'parking': True, 'pool': False, 'gym': False, 'restaurant': True, 'spa': False},
                'latitude': 27.1767,
                'longitude': 78.0081,
                'address': 'Taj Ganj, Agra',
                'contact_phone': '+91-562-222-3333',
                'contact_email': 'reservations.agra@tajhotels.com',
            },
            {
                'name': 'Lake Pichola Resort Udaipur',
                'city': 'Udaipur',
                'star_rating': 4,
                'review_rating': 4.5,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': False, 'restaurant': True, 'spa': False},
                'latitude': 24.5770,
                'longitude': 73.6800,
                'address': 'Lake Pichola, Udaipur',
                'contact_phone': '+91-294-252-1234',
                'contact_email': 'reservations.udaipur@lakehotels.com',
            },
            {
                'name': 'Taj Bengal Kolkata',
                'city': 'Kolkata',
                'star_rating': 5,
                'review_rating': 4.6,
                'amenities': {'wifi': True, 'parking': True, 'pool': True, 'gym': True, 'restaurant': True, 'spa': True},
                'latitude': 22.5490,
                'longitude': 88.3518,
                'address': 'Alipore, Kolkata',
                'contact_phone': '+91-33-2499-1234',
                'contact_email': 'reservations.guest@tajbengal.com',
            },
            {
                'name': 'Brunton Boatyard Kochi',
                'city': 'Kochi',
                'star_rating': 4,
                'review_rating': 4.3,
                'amenities': {'wifi': True, 'parking': True, 'pool': False, 'gym': False, 'restaurant': True, 'spa': False},
                'latitude': 9.9667,
                'longitude': 76.2833,
                'address': 'Fort Kochi, Kochi',
                'contact_phone': '+91-484-234-5678',
                'contact_email': 'reservations@bruntonboatyard.com',
            },
        ]

        # Room types config
        room_types_config = [
            {
                'name': 'Standard Room',
                'room_type': 'standard',
                'max_occupancy': 2,
                'number_of_beds': 1,
                'room_size': 300,
                'base_price': 8000,
                'total_rooms': 20,
            },
            {
                'name': 'Deluxe Room',
                'room_type': 'deluxe',
                'max_occupancy': 3,
                'number_of_beds': 1,
                'room_size': 450,
                'base_price': 15000,
                'total_rooms': 30,
            },
            {
                'name': 'Suite',
                'room_type': 'suite',
                'max_occupancy': 4,
                'number_of_beds': 2,
                'room_size': 800,
                'base_price': 35000,
                'total_rooms': 10,
            },
            {
                'name': 'Presidential Suite',
                'room_type': 'suite',
                'max_occupancy': 6,
                'number_of_beds': 3,
                'room_size': 1200,
                'base_price': 70000,
                'total_rooms': 2,
            },
        ]

        # Create hotels
        for hotel_data in hotels_data:
            hotel, created = Hotel.objects.get_or_create(
                name=hotel_data['name'],
                city=cities[hotel_data['city']],
                defaults={
                    'description': f"Luxury hotel in {hotel_data['city']}",
                    'address': hotel_data['address'],
                    'latitude': Decimal(str(hotel_data['latitude'])),
                    'longitude': Decimal(str(hotel_data['longitude'])),
                    'star_rating': hotel_data['star_rating'],
                    'review_rating': Decimal(str(hotel_data['review_rating'])),
                    'review_count': random.randint(500, 2000),
                    'has_wifi': hotel_data['amenities']['wifi'],
                    'has_parking': hotel_data['amenities']['parking'],
                    'has_pool': hotel_data['amenities']['pool'],
                    'has_gym': hotel_data['amenities']['gym'],
                    'has_restaurant': hotel_data['amenities']['restaurant'],
                    'has_spa': hotel_data['amenities']['spa'],
                    'is_featured': random.choice([True, False]),
                    'is_active': True,
                    'gst_percentage': Decimal('18.00'),
                    'contact_phone': hotel_data['contact_phone'],
                    'contact_email': hotel_data['contact_email'],
                }
            )
            
            if created:
                self.stdout.write(f'✓ Created hotel: {hotel.name}')
                
                # Create room types for this hotel
                for room_config in room_types_config:
                    room_type, _ = RoomType.objects.get_or_create(
                        hotel=hotel,
                        name=room_config['name'],
                        defaults={
                            'room_type': room_config['room_type'],
                            'description': f"{room_config['name']} in {hotel.name}",
                            'max_occupancy': room_config['max_occupancy'],
                            'number_of_beds': room_config['number_of_beds'],
                            'room_size': room_config['room_size'],
                            'base_price': Decimal(str(room_config['base_price'])),
                            'has_balcony': random.choice([True, False]),
                            'has_tv': True,
                            'has_minibar': room_config['room_type'] != 'standard',
                            'has_safe': True,
                            'total_rooms': room_config['total_rooms'],
                            'is_available': True,
                        }
                    )
                    
                    # Create availability records for next 30 days
                    start_date = date.today()
                    for i in range(30):
                        current_date = start_date + timedelta(days=i)
                        
                        # Dynamic pricing: peak on weekends
                        is_weekend = current_date.weekday() >= 4
                        price_multiplier = Decimal('1.2') if is_weekend else Decimal('1.0')
                        price = room_config['base_price'] * float(price_multiplier)
                        
                        # Availability varies
                        available_rooms = max(1, room_config['total_rooms'] - random.randint(0, 5))
                        
                        RoomAvailability.objects.get_or_create(
                            room_type=room_type,
                            date=current_date,
                            defaults={
                                'available_rooms': available_rooms,
                                'price': Decimal(str(price)),
                            }
                        )
                
                # Create discounts for this hotel
                next_month = timezone.now() + timedelta(days=30)
                
                discounts = [
                    {
                        'discount_type': 'percentage',
                        'discount_value': Decimal('20.00'),
                        'description': '20% off on all bookings',
                        'code': f'SAVE20_{hotel.id}',
                        'min_booking_amount': Decimal('50000.00'),
                        'max_discount': Decimal('10000.00'),
                    },
                    {
                        'discount_type': 'fixed',
                        'discount_value': Decimal('5000.00'),
                        'description': '₹5000 cashback',
                        'code': f'OFF5K_{hotel.id}',
                        'min_booking_amount': Decimal('30000.00'),
                    },
                    {
                        'discount_type': 'percentage',
                        'discount_value': Decimal('15.00'),
                        'description': '15% off for members',
                        'code': f'MEMBER15_{hotel.id}',
                        'min_booking_amount': Decimal('20000.00'),
                        'max_discount': Decimal('5000.00'),
                    },
                ]
                
                for discount_data in discounts:
                    HotelDiscount.objects.get_or_create(
                        hotel=hotel,
                        code=discount_data['code'],
                        defaults={
                            'discount_type': discount_data['discount_type'],
                            'discount_value': discount_data['discount_value'],
                            'description': discount_data['description'],
                            'valid_from': timezone.now(),
                            'valid_till': next_month,
                            'min_booking_amount': discount_data['min_booking_amount'],
                            'max_discount': discount_data.get('max_discount'),
                            'is_active': True,
                        }
                    )

        self.stdout.write(
            self.style.SUCCESS('\n✓ Successfully seeded hotel database!')
        )
        self.stdout.write(f'  • Created {len(hotels_data)} hotels')
        self.stdout.write(f'  • Created {len(room_types_config)} room types per hotel')
        self.stdout.write(f'  • Created 30 days of availability records')
        self.stdout.write(f'  • Created 3 discounts per hotel')
