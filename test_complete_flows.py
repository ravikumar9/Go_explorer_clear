"""
Comprehensive test script to verify all GoExplorer flows
Tests: Login, Bus Search, Hotel Search, Bookings, User Profile
"""
import os
import sys
import django
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goexplorer.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test.utils import setup_test_environment
from django.test.client import Client
from hotels.models import City
from buses.models import Bus, BusRoute
from bookings.models import Booking

User = get_user_model()

# Initialize test client
client = Client()

print("=" * 80)
print("GOEXPLORER COMPLETE FLOWS TEST")
print("=" * 80)
print()

# ============================================================================
# TEST 1: LOGIN
# ============================================================================
print("TEST 1: LOGIN FLOW")
print("-" * 80)

# Create test user if doesn't exist
test_user_email = 'testuser@example.com'
test_user_password = 'TestPassword123!'
try:
    test_user = User.objects.get(email=test_user_email)
    print(f"[OK] Test user exists: {test_user_email}")
except User.DoesNotExist:
    test_user = User.objects.create_user(
        username=test_user_email,
        email=test_user_email,
        password=test_user_password,
        first_name='Test',
        last_name='User',
        phone='9876543210'
    )
    print(f"[OK] Test user created: {test_user_email}")

# Test login page
response = client.get('/users/login/')
print(f"[{response.status_code}] GET /users/login/")
if response.status_code == 200:
    print("[OK] Login page loads successfully")
else:
    print("[ERROR] Login page failed to load")

# Test login POST
response = client.post('/users/login/', {
    'email': test_user_email,
    'password': test_user_password
})
print(f"[{response.status_code}] POST /users/login/ (valid credentials)")
if response.status_code in [200, 302]:  # 302 redirect on success
    if 'session' in client.cookies or response.wsgi_request.user.is_authenticated if hasattr(response, 'wsgi_request') else True:
        print("[OK] Login successful")
    else:
        print("[WARNING] Login may have failed (check redirect)")
else:
    print("[ERROR] Login failed")

print()

# ============================================================================
# TEST 2: BUS SEARCH
# ============================================================================
print("TEST 2: BUS SEARCH FLOW")
print("-" * 80)

# Test without search params
response = client.get('/buses/')
print(f"[{response.status_code}] GET /buses/ (no params)")
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    buses_found = len(soup.find_all('div', class_='bus-card'))
    print(f"[OK] Page loads, found {buses_found} buses without search params")
else:
    print("[ERROR] Bus list page failed")

# Test with search params
search_params = {
    'source_city': 'Bangalore',
    'dest_city': 'Mumbai',
    'travel_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
}
response = client.get('/buses/', search_params)
print(f"[{response.status_code}] GET /buses/ (with search: {search_params['source_city']} -> {search_params['dest_city']})")
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    buses_found = len(soup.find_all('div', class_='bus-card'))
    no_results = soup.find('div', class_='alert alert-info')
    
    if buses_found > 0:
        print(f"[OK] Found {buses_found} buses for search")
        for i, card in enumerate(soup.find_all('div', class_='bus-card')[:2], 1):
            operator = card.find('h5')
            price = card.find('div', class_='price-amount')
            op_name = operator.text if operator else 'N/A'
            price_text = price.text.replace('₹', 'Rs.') if price else 'N/A'
            print(f"     Bus {i}: {op_name} - {price_text}")
    elif no_results:
        print(f"[WARNING] No buses found: {no_results.text}")
    else:
        print("[ERROR] Unexpected result - no buses and no message")
else:
    print("[ERROR] Bus search failed")

print()

# ============================================================================
# TEST 3: BUS DETAIL & SEAT SELECTION
# ============================================================================
print("TEST 3: BUS DETAIL & SEAT LAYOUT")
print("-" * 80)

buses = Bus.objects.all()[:1]
if buses:
    bus = buses[0]
    route = bus.routes.first()
    if route:
        response = client.get(f'/buses/{bus.id}/', {
            'route_id': route.id,
            'travel_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        })
        print(f"[{response.status_code}] GET /buses/{bus.id}/ (seat layout page)")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for seat layout
            seat_divs = soup.find_all('div', class_='seat')
            print(f"[OK] Seat layout page loads, found {len(seat_divs)} seats")
            
            # Check for boarding/dropping dropdowns
            boarding_select = soup.find('select', {'name': 'boarding_point'})
            dropping_select = soup.find('select', {'name': 'dropping_point'})
            
            if boarding_select:
                boarding_options = boarding_select.find_all('option')
                print(f"[OK] Boarding points dropdown: {len(boarding_options)} options")
            else:
                print("[WARNING] Boarding points dropdown not found")
            
            if dropping_select:
                dropping_options = dropping_select.find_all('option')
                print(f"[OK] Dropping points dropdown: {len(dropping_options)} options")
            else:
                print("[WARNING] Dropping points dropdown not found")
        else:
            print("[ERROR] Bus detail page failed")
    else:
        print("[WARNING] No routes available for buses")
else:
    print("[WARNING] No buses in database")

print()

# ============================================================================
# TEST 4: HOTEL SEARCH
# ============================================================================
print("TEST 4: HOTEL SEARCH FLOW")
print("-" * 80)

response = client.get('/hotels/', {
    'city': 'Mumbai',
    'checkin': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
    'checkout': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
})
print(f"[{response.status_code}] GET /hotels/ (with search params)")
if response.status_code == 200:
    print("[OK] Hotel search page loads")
else:
    print("[ERROR] Hotel search page failed")

print()

# ============================================================================
# TEST 5: USER PROFILE
# ============================================================================
print("TEST 5: USER PROFILE")
print("-" * 80)

# Login first
client.login(email=test_user_email, password=test_user_password)

response = client.get('/users/profile/')
print(f"[{response.status_code}] GET /users/profile/ (authenticated)")
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    booking_table = soup.find('table')
    if booking_table:
        rows = booking_table.find_all('tr')[1:]  # Skip header
        print(f"[OK] User profile page loads, showing {len(rows)} bookings")
    else:
        print("[OK] User profile page loads (no bookings)")
else:
    print("[ERROR] User profile page failed")

print()

# ============================================================================
# TEST 6: LOGOUT
# ============================================================================
print("TEST 6: LOGOUT FLOW")
print("-" * 80)

response = client.get('/users/logout/')
print(f"[{response.status_code}] GET /users/logout/")
if response.status_code in [200, 302]:
    print("[OK] Logout successful")
else:
    print("[ERROR] Logout failed")

print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print("All critical flows tested. Check results above for any [ERROR] or [WARNING] items.")
print("=" * 80)
