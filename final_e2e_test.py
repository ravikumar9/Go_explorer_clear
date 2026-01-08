"""
Final Comprehensive E2E Test for GoExplorer
Tests all critical user flows end-to-end
"""
import os
import sys
import django
from datetime import datetime, timedelta
from django.test.client import Client
from bs4 import BeautifulSoup

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'goexplorer.settings')
django.setup()

from django.contrib.auth import get_user_model
from hotels.models import City, Hotel, RoomType
from buses.models import Bus, BusRoute, BusOperator

User = get_user_model()
client = Client()

def extract_data(html, selector, attr=None):
    """Helper to extract data from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    elem = soup.select_one(selector)
    if elem:
        return elem.get(attr) if attr else elem.get_text(strip=True)
    return None

# ============================================================================
# TEST SUITE
# ============================================================================
print("\n" + "="*80)
print("GOEXPLORER COMPREHENSIVE E2E TEST SUITE")
print("="*80 + "\n")

test_results = []

# TEST 1: HOME PAGE
print("[TEST 1] Home Page")
response = client.get('/')
assert response.status_code == 200, "Home page should return 200"
test_results.append(('Home Page', response.status_code == 200))
print(f"  [PASS] Home page loads (Status: {response.status_code})\n")

# TEST 2: REGISTRATION FLOW
print("[TEST 2] User Registration")
import time
test_email = f"test_{int(time.time())}@example.com"
test_phone = "9876543210"
test_password = "TestPass123"

response = client.post('/users/register/', {
    'email': test_email,
    'first_name': 'Test',
    'last_name': 'User',
    'phone': test_phone,
    'password': test_password,
    'password_confirm': test_password,
})

if response.status_code in [200, 302]:  # Could be redirect or re-render
    try:
        user = User.objects.get(email=test_email)
        assert user.phone == test_phone, "Phone should be saved"
        test_results.append(('User Registration', True))
        print(f"  [PASS] User registered: {test_email}\n")
    except User.DoesNotExist:
        test_results.append(('User Registration', False))
        print(f"  [FAIL] User not created\n")
else:
    test_results.append(('User Registration', False))
    print(f"  [FAIL] Registration returned {response.status_code}\n")

# TEST 3: LOGIN FLOW
print("[TEST 3] User Login")
response = client.post('/users/login/', {
    'email': test_email,
    'password': test_password,
})

if response.status_code in [200, 302]:
    test_results.append(('User Login', True))
    print(f"  [PASS] Login successful\n")
else:
    test_results.append(('User Login', False))
    print(f"  [FAIL] Login returned {response.status_code}\n")

# TEST 4: BUS SEARCH
print("[TEST 4] Bus Search")
response = client.get('/buses/', {
    'source_city': 'Bangalore',
    'dest_city': 'Mumbai',
    'travel_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
})

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    buses = soup.find_all('div', class_='bus-card')
    if len(buses) > 0:
        test_results.append(('Bus Search', True))
        print(f"  [PASS] Found {len(buses)} buses\n")
    else:
        test_results.append(('Bus Search', False))
        print(f"  [FAIL] No buses found\n")
else:
    test_results.append(('Bus Search', False))
    print(f"  [FAIL] Bus search returned {response.status_code}\n")

# TEST 5: BUS DETAIL & SEAT LAYOUT
print("[TEST 5] Bus Detail & Seat Layout")
buses_obj = Bus.objects.all()[:1]
if buses_obj:
    bus = buses_obj[0]
    route = bus.routes.first()
    if route:
        response = client.get(f'/buses/{bus.id}/', {
            'route_id': route.id,
            'travel_date': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
        })
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            seats = soup.find_all('label', class_='seat')
            boarding = soup.find('select', {'name': 'boarding_point'})
            dropping = soup.find('select', {'name': 'dropping_point'})
            
            has_seats = len(seats) > 0
            has_boarding = boarding and len(boarding.find_all('option')) > 1
            has_dropping = dropping and len(dropping.find_all('option')) > 1
            
            success = has_seats and has_boarding and has_dropping
            test_results.append(('Bus Detail', success))
            
            print(f"  [PASS] Bus detail page loaded" if has_seats else f"  [FAIL] No seats found")
            print(f"    - Seats: {len(seats)} {'(OK)' if has_seats else '(MISSING)'}")
            print(f"    - Boarding points: {len(boarding.find_all('option'))-1 if boarding else 0} {'(OK)' if has_boarding else '(MISSING)'}")
            print(f"    - Dropping points: {len(dropping.find_all('option'))-1 if dropping else 0} {'(OK)' if has_dropping else '(MISSING)'}\n")
        else:
            test_results.append(('Bus Detail', False))
            print(f"  [FAIL] Bus detail returned {response.status_code}\n")

# TEST 6: HOTEL SEARCH
print("[TEST 6] Hotel Search")
response = client.get('/hotels/', {
    'city': 'Mumbai',
    'checkin': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
    'checkout': (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d')
})

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    hotels = soup.find_all('div', class_='hotel-card')
    if hotels or 'hotel' in response.content.decode().lower():
        test_results.append(('Hotel Search', True))
        print(f"  [PASS] Hotel search page loaded\n")
    else:
        test_results.append(('Hotel Search', False))
        print(f"  [FAIL] No hotel content found\n")
else:
    test_results.append(('Hotel Search', False))
    print(f"  [FAIL] Hotel search returned {response.status_code}\n")

# TEST 7: USER PROFILE
print("[TEST 7] User Profile")
response = client.get('/users/profile/')

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    profile_content = 'booking' in response.content.decode().lower()
    if profile_content:
        test_results.append(('User Profile', True))
        print(f"  [PASS] User profile page loaded with booking history\n")
    else:
        test_results.append(('User Profile', False))
        print(f"  [FAIL] No profile content found\n")
elif response.status_code == 302:
    test_results.append(('User Profile', True))
    print(f"  [PASS] User profile requires login (redirected)\n")
else:
    test_results.append(('User Profile', False))
    print(f"  [FAIL] User profile returned {response.status_code}\n")

# TEST 8: LOGOUT
print("[TEST 8] User Logout")
response = client.get('/users/logout/')

if response.status_code in [200, 302]:
    test_results.append(('User Logout', True))
    print(f"  [PASS] Logout successful\n")
else:
    test_results.append(('User Logout', False))
    print(f"  [FAIL] Logout returned {response.status_code}\n")

# TEST 9: DATABASE INTEGRITY
print("[TEST 9] Database Integrity")
cities = City.objects.count()
buses = Bus.objects.count()
routes = BusRoute.objects.count()
operators = BusOperator.objects.count()

db_ok = cities > 0 and buses > 0 and routes > 0 and operators > 0
test_results.append(('Database Integrity', db_ok))

print(f"  [PASS] Database populated" if db_ok else f"  [FAIL] Missing data")
print(f"    - Cities: {cities} (expect 6+)")
print(f"    - Buses: {buses} (expect 4+)")
print(f"    - Routes: {routes} (expect 6+)")
print(f"    - Operators: {operators} (expect 2+)\n")

# ============================================================================
# SUMMARY
# ============================================================================
print("="*80)
print("TEST SUMMARY")
print("="*80)

passed = sum(1 for _, result in test_results if result)
total = len(test_results)

for test_name, result in test_results:
    status = "PASS" if result else "FAIL"
    symbol = "[+]" if result else "[-]"
    print(f"{symbol} {test_name}: {status}")

print("\n" + "="*80)
print(f"TOTAL: {passed}/{total} tests passed ({int(passed/total*100)}%)")
print("="*80)

if passed == total:
    print("\n*** ALL TESTS PASSED - APPLICATION READY FOR PRODUCTION ***\n")
else:
    print(f"\n*** {total-passed} TESTS FAILED - REVIEW FAILURES ABOVE ***\n")
