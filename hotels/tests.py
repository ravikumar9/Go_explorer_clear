"""
Hotel Backend Tests
Comprehensive testing for pricing, search, filter, and availability logic
"""

import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime, timedelta

from .models import Hotel, RoomType, RoomAvailability, HotelDiscount, City
from .pricing_service import PricingCalculator, OccupancyCalculator
from .serializers import HotelListSerializer, PricingRequestSerializer


class HotelTestSetup(TestCase):
    """Base test setup with sample data"""
    
    def setUp(self):
        """Create test data"""
        # Create city
        self.city = City.objects.create(
            name='Mumbai',
            state='Maharashtra',
            country='India'
        )
        
        # Create hotel
        self.hotel = Hotel.objects.create(
            name='Taj Mahal Palace',
            description='Luxury 5-star hotel',
            city=self.city,
            address='Apollo Bunder, Mumbai',
            latitude=Decimal('18.9520'),
            longitude=Decimal('72.8347'),
            star_rating=5,
            review_rating=Decimal('4.8'),
            review_count=1250,
            has_wifi=True,
            has_parking=True,
            has_pool=True,
            has_gym=True,
            has_restaurant=True,
            has_spa=True,
            gst_percentage=Decimal('18.00'),
            contact_phone='+91-22-6665-3366',
            contact_email='reservations@tajhotel.com'
        )
        
        # Create room types
        self.room_deluxe = RoomType.objects.create(
            hotel=self.hotel,
            name='Deluxe Room',
            room_type='deluxe',
            description='Luxurious deluxe room with sea view',
            max_occupancy=2,
            number_of_beds=1,
            room_size=450,
            base_price=Decimal('15000.00'),
            has_balcony=True,
            has_tv=True,
            has_minibar=True,
            has_safe=True,
            total_rooms=10,
            is_available=True
        )
        
        self.room_suite = RoomType.objects.create(
            hotel=self.hotel,
            name='Presidential Suite',
            room_type='suite',
            description='Grand presidential suite',
            max_occupancy=4,
            number_of_beds=2,
            room_size=800,
            base_price=Decimal('50000.00'),
            has_balcony=True,
            has_tv=True,
            has_minibar=True,
            has_safe=True,
            total_rooms=2,
            is_available=True
        )
        
        # Create room availability for next 30 days
        start_date = date.today()
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            
            # Deluxe availability
            RoomAvailability.objects.create(
                room_type=self.room_deluxe,
                date=current_date,
                available_rooms=8 if i % 7 < 5 else 5,  # Less availability on weekends
                price=Decimal('15000.00') if i % 7 < 5 else Decimal('18000.00')
            )
            
            # Suite availability
            RoomAvailability.objects.create(
                room_type=self.room_suite,
                date=current_date,
                available_rooms=2,
                price=Decimal('50000.00') if i % 7 < 5 else Decimal('60000.00')
            )
        
        # Create discounts
        tomorrow = timezone.now() + timedelta(days=1)
        next_month = timezone.now() + timedelta(days=30)
        
        self.discount_percentage = HotelDiscount.objects.create(
            hotel=self.hotel,
            discount_type='percentage',
            discount_value=Decimal('20.00'),
            description='20% off on all rooms',
            code='SAVE20',
            valid_from=timezone.now(),
            valid_till=next_month,
            min_booking_amount=Decimal('50000.00'),
            max_discount=Decimal('10000.00'),
            is_active=True
        )
        
        self.discount_fixed = HotelDiscount.objects.create(
            hotel=self.hotel,
            discount_type='fixed',
            discount_value=Decimal('5000.00'),
            description='₹5000 off on bookings',
            code='OFF5K',
            valid_from=timezone.now(),
            valid_till=next_month,
            min_booking_amount=Decimal('30000.00'),
            is_active=True
        )


# ============================================
# PRICING LOGIC TESTS
# ============================================

class PricingCalculatorTests(HotelTestSetup):
    """Test pricing calculations"""
    
    def test_basic_price_calculation(self):
        """Test basic price calculation without discounts"""
        calculator = PricingCalculator(self.hotel)
        
        check_in = date.today()
        check_out = check_in + timedelta(days=3)
        
        pricing = calculator.calculate_total_price(
            self.room_deluxe,
            check_in,
            check_out,
            num_rooms=1
        )
        
        # Assertions
        self.assertEqual(pricing['num_nights'], 3)
        self.assertEqual(pricing['num_rooms'], 1)
        self.assertEqual(pricing['base_price'], 15000.0)
        
        # Subtotal = base_price * nights * rooms
        expected_subtotal = 15000 * 3 * 1
        self.assertEqual(pricing['subtotal'], expected_subtotal)
        
        # GST = subtotal * 0.18
        expected_gst = expected_subtotal * 0.18
        self.assertAlmostEqual(pricing['gst_amount'], expected_gst, places=2)
        
        # Total = subtotal + gst
        expected_total = expected_subtotal + expected_gst
        self.assertAlmostEqual(pricing['total_amount'], expected_total, places=2)
    
    def test_price_calculation_multiple_rooms(self):
        """Test pricing for multiple rooms"""
        calculator = PricingCalculator(self.hotel)
        
        check_in = date.today()
        check_out = check_in + timedelta(days=2)
        
        pricing = calculator.calculate_total_price(
            self.room_deluxe,
            check_in,
            check_out,
            num_rooms=3
        )
        
        self.assertEqual(pricing['num_rooms'], 3)
        expected_subtotal = 15000 * 2 * 3  # base * nights * rooms
        self.assertEqual(pricing['subtotal'], expected_subtotal)
    
    def test_percentage_discount_application(self):
        """Test percentage discount calculation"""
        calculator = PricingCalculator(self.hotel)
        
        check_in = date.today()
        check_out = check_in + timedelta(days=5)  # 5 nights
        
        pricing = calculator.calculate_total_price(
            self.room_suite,  # ₹50,000/night * 5 nights = ₹250,000
            check_in,
            check_out,
            num_rooms=1,
            discount_code='SAVE20'
        )
        
        subtotal = pricing['subtotal']
        
        # 20% of ₹250,000 = ₹50,000, but max is ₹10,000
        expected_discount = min(subtotal * 0.20, 10000)
        self.assertAlmostEqual(pricing['discount_amount'], expected_discount, places=2)
        
        # Verify subtotal after discount
        expected_subtotal_after = subtotal - expected_discount
        self.assertAlmostEqual(
            pricing['subtotal_after_discount'],
            expected_subtotal_after,
            places=2
        )
    
    def test_fixed_discount_application(self):
        """Test fixed discount calculation"""
        calculator = PricingCalculator(self.hotel)
        
        check_in = date.today()
        check_out = check_in + timedelta(days=2)
        
        pricing = calculator.calculate_total_price(
            self.room_suite,  # ₹50,000/night
            check_in,
            check_out,
            num_rooms=1,
            discount_code='OFF5K'
        )
        
        # Fixed discount should be exactly ₹5,000
        self.assertEqual(pricing['discount_amount'], 5000.0)
    
    def test_invalid_discount_code(self):
        """Test handling of invalid discount code"""
        calculator = PricingCalculator(self.hotel)
        
        check_in = date.today()
        check_out = check_in + timedelta(days=2)
        
        pricing = calculator.calculate_total_price(
            self.room_deluxe,
            check_in,
            check_out,
            discount_code='INVALID'
        )
        
        # Should not apply any discount
        self.assertEqual(pricing['discount_amount'], 0.0)
        self.assertIn('error', pricing['discount_details'])
    
    def test_discount_minimum_booking_amount(self):
        """Test discount minimum booking amount condition"""
        calculator = PricingCalculator(self.hotel)
        
        # SAVE20 requires min ₹50,000
        # Deluxe room is only ₹15,000/night, so 1 night doesn't qualify
        check_in = date.today()
        check_out = check_in + timedelta(days=1)
        
        pricing = calculator.calculate_total_price(
            self.room_deluxe,  # ₹15,000
            check_in,
            check_out,
            discount_code='SAVE20'
        )
        
        # Should not apply discount due to min amount
        self.assertEqual(pricing['discount_amount'], 0.0)
    
    def test_gst_calculation(self):
        """Test GST calculation"""
        calculator = PricingCalculator(self.hotel)
        
        check_in = date.today()
        check_out = check_in + timedelta(days=3)
        
        pricing = calculator.calculate_total_price(
            self.room_deluxe,
            check_in,
            check_out,
            num_rooms=1
        )
        
        # GST should be 18% of subtotal (after discount if any)
        expected_gst = pricing['subtotal_after_discount'] * (18 / 100)
        self.assertAlmostEqual(pricing['gst_amount'], expected_gst, places=2)
    
    def test_price_with_all_parameters(self):
        """Test complete pricing with rooms, dates, and discount"""
        calculator = PricingCalculator(self.hotel)
        
        check_in = date.today()
        check_out = check_in + timedelta(days=4)  # 4 nights
        
        pricing = calculator.calculate_total_price(
            self.room_suite,  # ₹50,000/night
            check_in,
            check_out,
            num_rooms=2,
            discount_code='OFF5K'
        )
        
        # Verify calculation chain
        expected_subtotal = 50000 * 4 * 2  # ₹400,000
        self.assertEqual(pricing['subtotal'], expected_subtotal)
        
        # Fixed discount ₹5,000
        self.assertEqual(pricing['discount_amount'], 5000.0)
        
        # Subtotal after discount
        expected_after_discount = 400000 - 5000  # ₹395,000
        self.assertEqual(pricing['subtotal_after_discount'], expected_after_discount)
        
        # GST on final amount
        expected_gst = expected_after_discount * 0.18
        self.assertAlmostEqual(pricing['gst_amount'], expected_gst, places=2)
        
        # Total
        expected_total = expected_after_discount + expected_gst
        self.assertAlmostEqual(pricing['total_amount'], expected_total, places=2)


# ============================================
# AVAILABILITY TESTS
# ============================================

class AvailabilityTests(HotelTestSetup):
    """Test availability checking"""
    
    def test_check_availability_available(self):
        """Test checking availability for available dates"""
        calculator = PricingCalculator(self.hotel)
        
        check_in = date.today()
        check_out = check_in + timedelta(days=3)
        
        availability = calculator.check_availability(
            self.room_deluxe,
            check_in,
            check_out,
            num_rooms=2
        )
        
        self.assertTrue(availability['is_available'])
        self.assertGreaterEqual(availability['min_available_rooms'], 2)
    
    def test_check_availability_not_available(self):
        """Test checking availability when not enough rooms"""
        calculator = PricingCalculator(self.hotel)
        
        check_in = date.today()
        check_out = check_in + timedelta(days=3)
        
        # Request more rooms than available
        availability = calculator.check_availability(
            self.room_suite,  # Only 2 rooms total
            check_in,
            check_out,
            num_rooms=5
        )
        
        self.assertFalse(availability['is_available'])
        self.assertLess(availability['min_available_rooms'], 5)


# ============================================
# API ENDPOINT TESTS
# ============================================

class HotelSearchAPITests(HotelTestSetup):
    """Test hotel search and listing APIs"""
    
    def setUp(self):
        super().setUp()
        self.client = Client()
    
    def test_hotel_list_api(self):
        """Test /api/list/ endpoint"""
        response = self.client.get('/hotels/api/list/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertGreater(len(data['results']), 0)
    
    def test_hotel_search_filter_by_city(self):
        """Test hotel search filter by city (id)"""
        response = self.client.get(f'/hotels/api/search/?city_id={self.city.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Should find our hotel
        self.assertGreater(len(data.get('results', [])), 0)

    def test_hotel_search_filter_by_city_name(self):
        """Test hotel search filter by city using city name"""
        response = self.client.get(f'/hotels/api/search/?city_id={self.city.name}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Should find our hotel when filtering by name
        self.assertGreater(len(data.get('results', [])), 0)
    
    def test_hotel_search_filter_by_rating(self):
        """Test hotel search filter by star rating"""
        response = self.client.get('/hotels/api/search/?star_rating=5')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get('results', [])
        for hotel in results:
            self.assertEqual(hotel['star_rating'], 5)
    
    def test_hotel_search_filter_by_amenity(self):
        """Test hotel search filter by amenities"""
        response = self.client.get('/hotels/api/search/?has_pool=true')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Our hotel has pool, should be included
        results = data.get('results', [])
        self.assertGreater(len(results), 0)
    
    def test_hotel_search_sort_by_price_asc(self):
        """Test sorting by price ascending"""
        response = self.client.get('/hotels/api/search/?sort_by=price_asc')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        results = data.get('results', [])
        if len(results) > 1:
            # Check if sorted
            for i in range(len(results) - 1):
                self.assertLessEqual(
                    results[i]['min_price'],
                    results[i+1]['min_price']
                )
    
    def test_hotel_detail_api(self):
        """Test hotel detail API"""
        response = self.client.get(f'/hotels/api/{self.hotel.id}/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], self.hotel.id)
        self.assertEqual(data['name'], self.hotel.name)
        self.assertIn('room_types', data)


class PricingAPITests(HotelTestSetup):
    """Test pricing calculation API"""
    
    def setUp(self):
        super().setUp()
        self.client = Client()
    
    def test_calculate_price_endpoint(self):
        """Test POST /api/calculate-price/"""
        check_in = date.today()
        check_out = check_in + timedelta(days=3)
        
        payload = {
            'room_type_id': self.room_deluxe.id,
            'check_in': check_in.isoformat(),
            'check_out': check_out.isoformat(),
            'num_rooms': 1
        }
        
        response = self.client.post(
            '/hotels/api/calculate-price/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('pricing', data)
        pricing = data['pricing']
        self.assertEqual(pricing['num_nights'], 3)
        self.assertEqual(pricing['currency'], 'INR')


# ============================================
# HTML VIEW / INTEGRATION TESTS
# ============================================

class HotelHTMLViewTests(HotelTestSetup):
    """Tests for server-rendered hotel list/detail pages"""

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_hotel_list_handles_city_name_param(self):
        """Older clients sometimes send city names — view should accept names or ids"""
        response = self.client.get(f'/hotels/?city_id={self.city.name}')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Our seeded hotel should appear on the page
        self.assertIn(self.hotel.name, content)


class HomePageSelectTests(TestCase):
    """Home page UI tests for selects"""

    def setUp(self):
        self.client = Client()
        # Ensure at least one city exists
        from core.models import City
        City.objects.get_or_create(name='SampleCity', code='SMP', defaults={'state': 'State', 'is_popular': True})

    def test_home_city_select_values_are_ids(self):
        """Ensure the search selects use numeric IDs as option values (not names)"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        # Should not contain legacy name-based 'name="city"' input
        self.assertNotIn('name="city"', content)
        import re
        self.assertTrue(re.search(r'<select[^>]+id="hotelCity"[\s\S]*<option\s+value="\d+"', content))
    


# ============================================
# OCCUPANCY TESTS
# ============================================

class OccupancyTests(HotelTestSetup):
    """Test occupancy calculations"""
    
    def test_occupancy_calculation(self):
        """Test hotel occupancy calculation"""
        start_date = date.today()
        end_date = start_date + timedelta(days=5)
        
        occupancy = OccupancyCalculator.get_hotel_occupancy_summary(
            self.hotel,
            start_date,
            end_date
        )
        
        self.assertEqual(occupancy['hotel_id'], self.hotel.id)
        self.assertIn('occupancy_percentage', occupancy)
        self.assertGreaterEqual(occupancy['occupancy_percentage'], 0)
        self.assertLessEqual(occupancy['occupancy_percentage'], 100)


# ============================================
# EDGE CASES AND VALIDATION TESTS
# ============================================

class EdgeCaseTests(HotelTestSetup):
    """Test edge cases and validation"""
    
    def setUp(self):
        super().setUp()
        self.client = Client()
    
    def test_invalid_date_range(self):
        """Test error handling for invalid date range"""
        payload = {
            'room_type_id': self.room_deluxe.id,
            'check_in': date.today().isoformat(),
            'check_out': date.today().isoformat(),  # Same day
            'num_rooms': 1
        }
        
        response = self.client.post(
            '/hotels/api/calculate-price/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_negative_rooms(self):
        """Test validation for negative room count"""
        payload = {
            'room_type_id': self.room_deluxe.id,
            'check_in': date.today().isoformat(),
            'check_out': (date.today() + timedelta(days=2)).isoformat(),
            'num_rooms': -1
        }
        
        response = self.client.post(
            '/hotels/api/calculate-price/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_nonexistent_room_type(self):
        """Test error handling for nonexistent room type"""
        payload = {
            'room_type_id': 99999,
            'check_in': date.today().isoformat(),
            'check_out': (date.today() + timedelta(days=2)).isoformat(),
            'num_rooms': 1
        }
        
        response = self.client.post(
            '/hotels/api/calculate-price/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
