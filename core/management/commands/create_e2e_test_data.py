"""
Management command to create comprehensive test data for E2E testing
Includes: cities, operators, buses, routes, boarding/dropping points, seat layouts, schedules
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, timedelta, time
from decimal import Decimal
from buses.models import (
    BusOperator, Bus, BusRoute, BoardingPoint, DroppingPoint, 
    SeatLayout, BusSchedule, BusStop
)
from hotels.models import City
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Create comprehensive E2E test data (cities, operators, buses, routes, seats, schedules)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Delete existing test data before creating new data',
        )

    def handle(self, *args, **options):
        if options['clean']:
            self.stdout.write("Cleaning existing test data...")
            self.clean_data()

        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('E2E TEST DATA CREATION'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        try:
            # Step 1: Create Cities
            cities = self.create_cities()
            
            # Step 2: Create Bus Operators
            operators = self.create_operators()
            
            # Step 3: Create Buses
            buses = self.create_buses(operators)
            
            # Step 4: Create Routes
            routes = self.create_routes(buses, cities)
            
            # Step 5: Create Boarding & Dropping Points
            self.create_boarding_dropping_points(routes, cities)
            
            # Step 6: Create Seat Layouts
            self.create_seat_layouts(buses)
            
            # Step 7: Create Schedules
            self.create_schedules(routes)
            
            # Summary
            self.print_summary(cities, operators, buses, routes)
            
            self.stdout.write(self.style.SUCCESS('\n' + '='*70))
            self.stdout.write(self.style.SUCCESS('[OK] TEST DATA CREATED SUCCESSFULLY'))
            self.stdout.write(self.style.SUCCESS('='*70 + '\n'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nX Error creating test data: {str(e)}\n'))
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def clean_data(self):
        """Delete test data in correct FK dependency order"""
        try:
            from django.db import transaction
            with transaction.atomic():
                # Delete in reverse dependency order
                BusSchedule.objects.all().delete()
                DroppingPoint.objects.all().delete()
                BoardingPoint.objects.all().delete()
                BusStop.objects.all().delete()
                SeatLayout.objects.all().delete()
                BusRoute.objects.all().delete()
                Bus.objects.all().delete()
                BusOperator.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('[OK] Cleaned existing data'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Warning during cleanup: {e}'))

    def create_cities(self):
        """Create Indian cities"""
        self.stdout.write('\n1. Creating Cities...')
        cities_data = [
            {'name': 'Bangalore', 'state': 'Karnataka', 'code': 'BLR'},
            {'name': 'Hyderabad', 'state': 'Telangana', 'code': 'HYD'},
            {'name': 'Mumbai', 'state': 'Maharashtra', 'code': 'MUM'},
            {'name': 'Chennai', 'state': 'Tamil Nadu', 'code': 'MAA'},
            {'name': 'Delhi', 'state': 'Delhi', 'code': 'DEL'},
            {'name': 'Pune', 'state': 'Maharashtra', 'code': 'PNQ'},
        ]
        
        cities = {}
        for data in cities_data:
            city, created = City.objects.get_or_create(code=data['code'], defaults=data)
            cities[data['code']] = city
            status = 'Created' if created else 'Exists'
            self.stdout.write(f"  [OK] {city.name} ({status})")
        
        return cities

    def create_operators(self):
        """Create bus operators"""
        self.stdout.write('\n2. Creating Bus Operators...')
        operators_data = [
            {
                'name': 'Interstate Travels',
                'contact_phone': '+918765432101',
                'contact_email': 'ops1@interstate.com',
                'description': 'Premium bus service connecting major cities'
            },
            {
                'name': 'Express Routes Ltd',
                'contact_phone': '+918765432102',
                'contact_email': 'ops2@express.com',
                'description': 'Budget-friendly long-distance bus operator'
            },
        ]
        
        operators = {}
        for data in operators_data:
            op, created = BusOperator.objects.get_or_create(
                name=data['name'],
                defaults={
                    'contact_phone': data['contact_phone'],
                    'contact_email': data['contact_email'],
                    'description': data['description'],
                    'is_active': True,
                    'verification_status': 'verified'
                }
            )
            operators[data['name']] = op
            status = 'Created' if created else 'Exists'
            self.stdout.write(f"  [OK] {op.name} - {op.contact_phone} ({status})")
        
        return operators

    def create_buses(self, operators):
        """Create buses for operators"""
        self.stdout.write('\n3. Creating Buses...')
        buses_data = [
            {
                'operator_name': 'Interstate Travels',
                'bus_number': 'KA-01-AB-2024',
                'bus_name': 'Interstate Volvo AC',
                'bus_type': 'volvo',
                'total_seats': 48,
                'amenities': {
                    'has_ac': True, 'has_wifi': True, 'has_charging_point': True,
                    'has_blanket': True, 'has_water_bottle': True, 'has_tv': True
                }
            },
            {
                'operator_name': 'Interstate Travels',
                'bus_number': 'KA-01-CD-2024',
                'bus_name': 'Interstate AC Sleeper',
                'bus_type': 'ac_sleeper',
                'total_seats': 40,
                'amenities': {
                    'has_ac': True, 'has_wifi': True, 'has_charging_point': True,
                    'has_blanket': True, 'has_water_bottle': True
                }
            },
            {
                'operator_name': 'Express Routes Ltd',
                'bus_number': 'TN-01-EF-2024',
                'bus_name': 'Express Non-AC Seater',
                'bus_type': 'seater',
                'total_seats': 60,
                'amenities': {
                    'has_wifi': True, 'has_water_bottle': True
                }
            },
            {
                'operator_name': 'Express Routes Ltd',
                'bus_number': 'TN-01-GH-2024',
                'bus_name': 'Express AC Seater',
                'bus_type': 'ac_seater',
                'total_seats': 52,
                'amenities': {
                    'has_ac': True, 'has_wifi': True, 'has_charging_point': True
                }
            },
        ]
        
        buses = []
        for data in buses_data:
            operator = operators[data['operator_name']]
            bus, created = Bus.objects.get_or_create(
                bus_number=data['bus_number'],
                defaults={
                    'operator': operator,
                    'bus_name': data['bus_name'],
                    'bus_type': data['bus_type'],
                    'total_seats': data['total_seats'],
                    'is_active': True,
                    'manufacturing_year': 2024,
                    **data['amenities']
                }
            )
            buses.append(bus)
            status = 'Created' if created else 'Exists'
            self.stdout.write(
                f"  [OK] {bus.bus_number} - {bus.bus_name} ({data['bus_type']}) - "
                f"{bus.total_seats} seats ({status})"
            )
        
        return buses

    def create_routes(self, buses, cities):
        """Create routes"""
        self.stdout.write('\n4. Creating Routes...')
        
        routes_data = [
            {
                'bus': buses[0],
                'source': 'BLR',
                'dest': 'HYD',
                'route_name': 'Bangalore to Hyderabad Express',
                'departure': '20:00',
                'arrival': '08:00',
                'duration': 12,
                'distance': 560,
                'base_fare': 1500
            },
            {
                'bus': buses[0],
                'source': 'BLR',
                'dest': 'MUM',
                'route_name': 'Bangalore to Mumbai Express',
                'departure': '18:00',
                'arrival': '06:00',
                'duration': 12,
                'distance': 980,
                'base_fare': 1800
            },
            {
                'bus': buses[1],
                'source': 'BLR',
                'dest': 'DEL',
                'route_name': 'Bangalore to Delhi AC Sleeper',
                'departure': '08:00',
                'arrival': '20:00',
                'duration': 32,
                'distance': 2150,
                'base_fare': 2500
            },
            {
                'bus': buses[2],
                'source': 'MUM',
                'dest': 'BLR',
                'route_name': 'Mumbai to Bangalore Economy',
                'departure': '22:00',
                'arrival': '10:00',
                'duration': 12,
                'distance': 980,
                'base_fare': 1200
            },
            {
                'bus': buses[2],
                'source': 'HYD',
                'dest': 'MAA',
                'route_name': 'Hyderabad to Chennai Budget',
                'departure': '10:00',
                'arrival': '18:00',
                'duration': 8,
                'distance': 570,
                'base_fare': 800
            },
            {
                'bus': buses[3],
                'source': 'DEL',
                'dest': 'PNQ',
                'route_name': 'Delhi to Pune AC Seater',
                'departure': '08:00',
                'arrival': '18:00',
                'duration': 24,
                'distance': 1440,
                'base_fare': 1600
            },
        ]
        
        routes = []
        for data in routes_data:
            route, created = BusRoute.objects.get_or_create(
                bus=data['bus'],
                source_city=cities[data['source']],
                destination_city=cities[data['dest']],
                defaults={
                    'route_name': data['route_name'],
                    'departure_time': time.fromisoformat(data['departure']),
                    'arrival_time': time.fromisoformat(data['arrival']),
                    'duration_hours': Decimal(str(data['duration'])),
                    'distance_km': Decimal(str(data['distance'])),
                    'base_fare': Decimal(str(data['base_fare'])),
                    'is_active': True,
                }
            )
            routes.append(route)
            status = 'Created' if created else 'Exists'
            self.stdout.write(
                f"  [OK] {data['source']} -> {data['dest']} | "
                f"{data['departure']}-{data['arrival']} | Rs.{data['base_fare']} ({status})"
            )
        
        return routes

    def create_boarding_dropping_points(self, routes, cities):
        """Create boarding and dropping points"""
        self.stdout.write('\n5. Creating Boarding & Dropping Points...')
        
        boarding_data = {
            'BLR': [
                {'name': 'Majestic Bus Stand', 'time': '20:00'},
                {'name': 'Electronic City', 'time': '20:30'},
            ],
            'HYD': [
                {'name': 'MGBS Hyderabad', 'time': '10:00'},
                {'name': 'Ameerpet Station', 'time': '10:45'},
            ],
            'MUM': [
                {'name': 'Central Bus Terminal', 'time': '22:00'},
                {'name': 'Dadar Station Pickup', 'time': '22:30'},
            ],
            'MAA': [
                {'name': 'Chennai Central', 'time': '10:00'},
                {'name': 'Mofussil Bus Stand', 'time': '10:45'},
            ],
            'DEL': [
                {'name': 'ISBT New Delhi', 'time': '08:00'},
                {'name': 'Kasol Gate', 'time': '08:30'},
            ],
            'PNQ': [
                {'name': 'Pune Bus Station', 'time': '08:00'},
                {'name': 'Sadashiv Peth', 'time': '08:45'},
            ],
        }
        
        dropping_data = {
            'BLR': [
                {'name': 'Majestic Bus Stand', 'time': '08:00'},
                {'name': 'Electronic City', 'time': '08:30'},
            ],
            'HYD': [
                {'name': 'MGBS Hyderabad', 'time': '08:00'},
                {'name': 'Ameerpet Station', 'time': '08:45'},
            ],
            'MUM': [
                {'name': 'Central Bus Terminal', 'time': '10:00'},
                {'name': 'Dadar Station Drop', 'time': '10:30'},
            ],
            'MAA': [
                {'name': 'Chennai Central', 'time': '18:00'},
                {'name': 'Mofussil Bus Stand', 'time': '18:45'},
            ],
            'DEL': [
                {'name': 'ISBT New Delhi', 'time': '20:00'},
                {'name': 'Kasol Gate', 'time': '20:30'},
            ],
            'PNQ': [
                {'name': 'Pune Bus Station', 'time': '18:00'},
                {'name': 'Sadashiv Peth', 'time': '18:45'},
            ],
        }
        
        count_created = 0
        count_existing = 0
        for route in routes:
            source_code = route.source_city.code
            dest_code = route.destination_city.code
            
            # Create boarding points
            for idx, bp_data in enumerate(boarding_data.get(source_code, []), 1):
                _, created = BoardingPoint.objects.get_or_create(
                    route=route,
                    name=bp_data['name'],
                    defaults={
                        'city': route.source_city,
                        'address': f'{bp_data["name"]}, {route.source_city.name}',
                        'pickup_time': time.fromisoformat(bp_data['time']),
                        'sequence_order': idx,
                        'is_active': True,
                    }
                )
                if created:
                    count_created += 1
                else:
                    count_existing += 1
            
            # Create dropping points
            for idx, dp_data in enumerate(dropping_data.get(dest_code, []), 1):
                _, created = DroppingPoint.objects.get_or_create(
                    route=route,
                    name=dp_data['name'],
                    defaults={
                        'city': route.destination_city,
                        'address': f'{dp_data["name"]}, {route.destination_city.name}',
                        'drop_time': time.fromisoformat(dp_data['time']),
                        'sequence_order': idx,
                        'is_active': True,
                    }
                )
                if created:
                    count_created += 1
                else:
                    count_existing += 1
        
        grand_total = count_created + count_existing
        self.stdout.write(f"  [OK] Boarding/Dropping - New: {count_created}, Existing: {count_existing}, Total in DB: {grand_total}")

    def create_seat_layouts(self, buses):
        """Create seat layouts for all buses based on bus_type"""
        self.stdout.write('\n6. Creating Seat Layouts...')
        
        total_created = 0
        total_existing = 0
        for bus in buses:
            seat_count_created = 0
            seat_count_existing = 0
            
            # Determine layout based on bus_type
            if bus.bus_type in ['seater', 'ac_seater']:
                # SEATER: 3+2 layout (5 seats per row)
                # Row configuration: [Window][Aisle][Window] | [Aisle][Window]
                seats_per_row = 5
                for seat_num in range(1, bus.total_seats + 1):
                    row = ((seat_num - 1) // seats_per_row) + 1
                    col = ((seat_num - 1) % seats_per_row) + 1
                    
                    # Reserve every 5th seat for ladies
                    reserved_for = 'ladies' if seat_num % 5 == 0 else 'general'
                    
                    _, created = SeatLayout.objects.get_or_create(
                        bus=bus,
                        seat_number=f'{seat_num}',
                        defaults={
                            'seat_type': 'seater',
                            'row': row,
                            'column': col,
                            'deck': 1,
                            'reserved_for': reserved_for,
                        }
                    )
                    if created:
                        seat_count_created += 1
                    else:
                        seat_count_existing += 1
                
            elif bus.bus_type in ['sleeper', 'ac_sleeper', 'volvo']:
                # SLEEPER: Lower deck + Upper deck
                # Split seats: 50% lower, 50% upper
                half = bus.total_seats // 2
                
                for seat_num in range(1, bus.total_seats + 1):
                    if seat_num <= half:
                        # Lower deck
                        deck = 1
                        seat_type = 'sleeper_lower'
                        row = ((seat_num - 1) // 2) + 1
                        col = ((seat_num - 1) % 2) + 1
                    else:
                        # Upper deck
                        deck = 2
                        seat_type = 'sleeper_upper'
                        adjusted = seat_num - half
                        row = ((adjusted - 1) // 2) + 1
                        col = ((adjusted - 1) % 2) + 1
                    
                    # Reserve every 5th seat for ladies
                    reserved_for = 'ladies' if seat_num % 5 == 0 else 'general'
                    
                    _, created = SeatLayout.objects.get_or_create(
                        bus=bus,
                        seat_number=f'{seat_num}',
                        defaults={
                            'seat_type': seat_type,
                            'row': row,
                            'column': col,
                            'deck': deck,
                            'reserved_for': reserved_for,
                        }
                    )
                    if created:
                        seat_count_created += 1
                    else:
                        seat_count_existing += 1
                        
            else:
                # Default fallback
                for seat_num in range(1, bus.total_seats + 1):
                    row = ((seat_num - 1) // 4) + 1
                    col = ((seat_num - 1) % 4) + 1
                    reserved_for = 'ladies' if seat_num % 5 == 0 else 'general'
                    
                    _, created = SeatLayout.objects.get_or_create(
                        bus=bus,
                        seat_number=f'{seat_num}',
                        defaults={
                            'seat_type': 'seater',
                            'row': row,
                            'column': col,
                            'deck': 1,
                            'reserved_for': reserved_for,
                        }
                    )
                    if created:
                        seat_count_created += 1
                    else:
                        seat_count_existing += 1
            
            total = seat_count_created + seat_count_existing
            status = f"New: {seat_count_created}, Existing: {seat_count_existing}, Total: {total}"
            self.stdout.write(f"  [OK] {bus.bus_number} ({bus.bus_type}) - {status}")
            total_created += seat_count_created
            total_existing += seat_count_existing
        
        grand_total = total_created + total_existing
        self.stdout.write(f"  [OK] Seats - New: {total_created}, Existing: {total_existing}, Total in DB: {grand_total}")

    def create_schedules(self, routes):
        """Create schedules for next 30 days"""
        self.stdout.write('\n7. Creating Schedules (Next 30 Days)...')
        
        total_created = 0
        total_existing = 0
        today = date.today()
        
        for route in routes:
            schedule_count_created = 0
            schedule_count_existing = 0
            for days_ahead in range(30):
                schedule_date = today + timedelta(days=days_ahead)
                
                _, created = BusSchedule.objects.get_or_create(
                    route=route,
                    date=schedule_date,
                    defaults={
                        'available_seats': route.bus.total_seats,
                        'booked_seats': 0,
                        'fare': route.base_fare,
                        'is_active': True,
                        'is_cancelled': False,
                    }
                )
                if created:
                    schedule_count_created += 1
                else:
                    schedule_count_existing += 1
            
            total = schedule_count_created + schedule_count_existing
            status = f"New: {schedule_count_created}, Existing: {schedule_count_existing}"
            self.stdout.write(
                f"  [OK] {route.source_city.code}->{route.destination_city.code} | {status}"
            )
            total_created += schedule_count_created
            total_existing += schedule_count_existing
        
        grand_total = total_created + total_existing
        self.stdout.write(f"  [OK] Schedules - New: {total_created}, Existing: {total_existing}, Total in DB: {grand_total}")

    def print_summary(self, cities, operators, buses, routes):
        """Print data summary"""
        self.stdout.write('\n' + '='*70)
        self.stdout.write('DATABASE SUMMARY (Current State)')
        self.stdout.write('='*70)
        self.stdout.write(f"  • Cities: {City.objects.count()}")
        self.stdout.write(f"  • Operators: {BusOperator.objects.count()}")
        self.stdout.write(f"  • Buses: {Bus.objects.count()}")
        self.stdout.write(f"  • Routes: {BusRoute.objects.count()}")
        self.stdout.write(f"  • Boarding Points: {BoardingPoint.objects.count()}")
        self.stdout.write(f"  • Dropping Points: {DroppingPoint.objects.count()}")
        self.stdout.write(f"  • Seat Layouts: {SeatLayout.objects.count()}")
        self.stdout.write(f"  • Schedules: {BusSchedule.objects.count()}")
        
        # Critical checks
        issues = []
        if SeatLayout.objects.count() == 0:
            issues.append("NO SEATS - Bookings will FAIL")
        if BusSchedule.objects.count() == 0:
            issues.append("NO SCHEDULES - Search will return EMPTY")
        if BoardingPoint.objects.count() == 0:
            issues.append("NO BOARDING POINTS - Booking form will BREAK")
        
        if issues:
            self.stdout.write('\n' + '='*70)
            self.stdout.write(self.style.ERROR('CRITICAL ISSUES DETECTED:'))
            for issue in issues:
                self.stdout.write(self.style.ERROR(f"  X {issue}"))
            self.stdout.write('='*70)
            self.stdout.write(self.style.WARNING('\nRun with --clean to delete and recreate all data'))
        else:
            self.stdout.write(f'\n{self.style.SUCCESS("All data looks good - booking flow should work")}')
