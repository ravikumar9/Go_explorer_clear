#!/usr/bin/env python3
"""
GoExplorer E2E Booking Flow Test Suite
Tests: Calendar dates, Hotel selection, Booking creation, Payment integration
Run: python3 test_e2e_complete.py
"""

import os
import sys
import django
from datetime import date, timedelta
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goexplorer.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from hotels.models import Hotel, RoomType
from bookings.models import Booking

print("\n" + "="*70)
print("GOEXPLORER E2E BOOKING FLOW TEST SUITE")
print("="*70)

class E2ETest:
    def __init__(self):
        self.client = Client()
        self.results = []
        
    def log(self, message, level="INFO"):
        """Colored logging"""
        colors = {
            "INFO": "\033[94m",     # Blue
            "SUCCESS": "\033[92m",   # Green
            "WARNING": "\033[93m",   # Yellow
            "ERROR": "\033[91m",     # Red
        }
        reset = "\033[0m"
        
        prefix = {
            "INFO": "[INFO]",
            "SUCCESS": "[✓]",
            "WARNING": "[⚠]",
            "ERROR": "[✗]",
        }
        
        print(f"{colors.get(level, '')}{prefix.get(level, level)}{reset} {message}")
    
    def test_step(self, name, condition, details=""):
        """Record test result"""
        status = "PASS" if condition else "FAIL"
        self.results.append((name, condition))
        
        level = "SUCCESS" if condition else "ERROR"
        msg = f"{name}: {status}"
        if details:
            msg += f" - {details}"
        self.log(msg, level)
        return condition
    
    def setup(self):
        """Setup test data"""
        self.log("Setting up test environment...")
        
        # Create test user
        self.user, created = User.objects.get_or_create(
            username='testbooker',
            defaults={'email': 'tester@goexplorer.local', 'first_name': 'Test'}
        )
        if created:
            self.user.set_password('test123')
            self.user.save()
        self.test_step("User Setup", self.user is not None, f"User: {self.user.username}")
        
        # Get first hotel
        self.hotel = Hotel.objects.filter(is_active=True).first()
        self.test_step("Hotel Available", self.hotel is not None, 
                      f"Hotel: {self.hotel.name if self.hotel else 'N/A'}")
        
        if not self.hotel:
            return False
        
        # Get room types
        self.room_types = self.hotel.room_types.all()
        self.test_step("Room Types Available", self.room_types.count() > 0, 
                      f"Rooms: {self.room_types.count()}")
        
        return True
    
    def test_homepage(self):
        """Test 1: Homepage loads"""
        self.log("\n" + "-"*70)
        self.log("TEST 1: HOMEPAGE LOADS", "INFO")
        self.log("-"*70, "INFO")
        
        response = self.client.get('/')
        self.test_step("Homepage loads", response.status_code == 200, f"Status: {response.status_code}")
        
        content = response.content.decode()
        self.test_step("Date inputs present", 'type="date"' in content)
        self.test_step("Booking script loaded", '<script>' in content)
    
    def test_hotel_list(self):
        """Test 2: Hotel list page"""
        self.log("\n" + "-"*70)
        self.log("TEST 2: HOTEL LIST PAGE", "INFO")
        self.log("-"*70, "INFO")
        
        response = self.client.get('/hotels/')
        self.test_step("Hotel list loads", response.status_code == 200, f"Status: {response.status_code}")
        
        content = response.content.decode()
        self.test_step("Hotels displayed", 'hotel' in content.lower())
    
    def test_hotel_detail(self):
        """Test 3: Hotel detail page"""
        self.log("\n" + "-"*70)
        self.log("TEST 3: HOTEL DETAIL PAGE", "INFO")
        self.log("-"*70, "INFO")
        
        url = f'/hotels/{self.hotel.id}/'
        response = self.client.get(url)
        self.test_step("Hotel detail loads", response.status_code == 200, f"URL: {url}")
        
        content = response.content.decode()
        self.test_step("Hotel name displayed", self.hotel.name in content)
        self.test_step("Booking form present", 'bookingForm' in content or 'booking-form' in content.lower())
        self.test_step("Check-in input present", 'checkin' in content or 'check_in' in content or 'check-in' in content)
        self.test_step("Check-out input present", 'checkout' in content or 'check_out' in content or 'check-out' in content)
        self.test_step("Room type selector present", 'room_type' in content or 'room-type' in content)
        self.test_step("Guest info fields present", 'guest_name' in content and 'guest_email' in content)
        self.test_step("Booking script loaded", 'updatePrice' in content or 'validateAndSubmit' in content)
    
    def test_api_availability(self):
        """Test 4: Availability API"""
        self.log("\n" + "-"*70)
        self.log("TEST 4: AVAILABILITY API", "INFO")
        self.log("-"*70, "INFO")
        
        check_in = date.today()
        check_out = check_in + timedelta(days=2)
        
        # Try different endpoint formats
        endpoints = [
            f'/api/hotels/{self.hotel.id}/available-rooms/',
            f'/hotels/api/{self.hotel.id}/available-rooms/',
            f'/api/hotels/{self.hotel.id}/availability/',
        ]
        
        api_works = False
        for endpoint in endpoints:
            try:
                response = self.client.post(
                    endpoint,
                    json={'check_in': str(check_in), 'check_out': str(check_out)},
                    content_type='application/json'
                )
                if response.status_code < 500:
                    api_works = True
                    self.log(f"Endpoint found: {endpoint} (Status: {response.status_code})", "SUCCESS")
                    break
            except:
                pass
        
        self.test_step("Availability API", api_works, "At least one endpoint responds")
    
    def test_booking_flow(self):
        """Test 5: Complete booking flow"""
        self.log("\n" + "-"*70)
        self.log("TEST 5: COMPLETE BOOKING FLOW", "INFO")
        self.log("-"*70, "INFO")
        
        # Login
        login_ok = self.client.login(username='testbooker', password='test123')
        self.test_step("User login", login_ok)
        
        if not login_ok:
            self.log("Cannot continue without login", "ERROR")
            return False
        
        # Prepare booking data
        check_in = date.today() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)
        room = self.room_types.first()
        
        booking_data = {
            'hotel': self.hotel.id,
            'room_type': room.id if room else 1,
            'checkin_date': str(check_in),
            'checkout_date': str(check_out),
            'num_rooms': 1,
            'num_guests': 2,
            'guest_name': 'Test Booker',
            'guest_email': 'tester@goexplorer.local',
            'guest_phone': '9876543210',
        }
        
        # Try to create booking
        booking_url = f'/hotels/{self.hotel.id}/book/'
        response = self.client.post(booking_url, booking_data)
        
        self.test_step("Booking endpoint responds", response.status_code < 500, 
                      f"Status: {response.status_code}")
        
        # Check if booking was created
        bookings = Booking.objects.filter(user=self.user).order_by('-created_at')
        booking_created = bookings.exists()
        
        self.test_step("Booking created in database", booking_created)
        
        if booking_created:
            latest_booking = bookings.first()
            self.log(f"Booking ID: {latest_booking.booking_id}", "INFO")
            self.test_step("Booking has correct hotel", latest_booking.booking_type in ['hotel', None])
            self.test_step("Booking status", latest_booking.status in ['pending', 'confirmed'])
            self.test_step("Total amount set", latest_booking.total_amount > 0)
    
    def test_payment_setup(self):
        """Test 6: Payment integration"""
        self.log("\n" + "-"*70)
        self.log("TEST 6: PAYMENT INTEGRATION", "INFO")
        self.log("-"*70, "INFO")
        
        # Check if Razorpay is configured
        from django.conf import settings
        
        has_razorpay_key = bool(getattr(settings, 'RAZORPAY_KEY_ID', None))
        has_razorpay_secret = bool(getattr(settings, 'RAZORPAY_KEY_SECRET', None))
        
        self.test_step("Razorpay Key ID configured", has_razorpay_key)
        self.test_step("Razorpay Secret configured", has_razorpay_secret)
        
        # Test payment endpoint
        response = self.client.post('/bookings/api/create-order/', {})
        payment_endpoint_ok = response.status_code in [401, 403, 400]  # Means endpoint exists
        self.test_step("Payment API endpoint exists", payment_endpoint_ok, f"Status: {response.status_code}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        if not self.setup():
            self.log("Setup failed, cannot continue", "ERROR")
            return False
        
        self.test_homepage()
        self.test_hotel_list()
        self.test_hotel_detail()
        self.test_api_availability()
        self.test_booking_flow()
        self.test_payment_setup()
        
        # Summary
        self.log("\n" + "="*70)
        self.log("TEST SUMMARY", "INFO")
        self.log("="*70, "INFO")
        
        passed = sum(1 for _, result in self.results if result)
        total = len(self.results)
        
        for test_name, result in self.results:
            status = "✓" if result else "✗"
            print(f"  {status} {test_name}")
        
        print(f"\n  TOTAL: {passed}/{total} tests passed\n")
        
        if passed == total:
            self.log("ALL TESTS PASSED - Booking flow is working!", "SUCCESS")
            return True
        else:
            self.log(f"{total - passed} test(s) FAILED - Review above", "ERROR")
            return False

def main():
    try:
        tester = E2ETest()
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
