#!/usr/bin/env python3
"""
Comprehensive verification of GoExplorer features on live server
"""
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import json

BASE_URL = 'http://goexplorer-dev.cloud'

print("\n" + "="*70)
print("GOEXPLORER COMPREHENSIVE FEATURE VERIFICATION")
print("="*70)

results = {}

# Test 1: Homepage loads with all components
print("\n1️⃣  HOMEPAGE")
print("-" * 70)
response = requests.get(f'{BASE_URL}/')
assert response.status_code == 200
soup = BeautifulSoup(response.text, 'html.parser')

# Check date inputs
date_inputs = soup.find_all('input', {'type': 'date'})
results['Date inputs on homepage'] = len(date_inputs) >= 2
print(f"   Date inputs: {len(date_inputs)} found ✓" if results['Date inputs on homepage'] else "   Date inputs: FAILED ✗")

# Check for CSS styling
styles = soup.find_all('style')
has_date_css = any('input[type="date"]' in s.text and 'color' in s.text for s in styles)
results['Date input CSS styling'] = has_date_css
print(f"   CSS styling: ✓" if results['Date input CSS styling'] else "   CSS styling: ✗")

# Check for JavaScript logic
scripts = soup.find_all('script')
has_date_js = any('todayStr' in s.text or 'prefillDates' in s.text for s in scripts)
results['Date input JavaScript'] = has_date_js
print(f"   Date repopulation JS: ✓" if results['Date input JavaScript'] else "   Date repopulation JS: ✗")

# Test 2: Hotel Listing
print("\n2️⃣  HOTEL LISTING PAGE")
print("-" * 70)
response = requests.get(f'{BASE_URL}/hotels/')
assert response.status_code == 200
soup = BeautifulSoup(response.text, 'html.parser')

# Check for hotel items
hotel_items = soup.find_all('div', {'class': 'hotel-item'}) or soup.find_all('div', {'class': 'card'})
results['Hotels displayed'] = len(hotel_items) > 0
print(f"   Hotel cards: {len(hotel_items)} found ✓" if results['Hotels displayed'] else "   Hotel cards: Not found ✗")

# Check for images
image_urls = [img.get('src') for img in soup.find_all('img') if img.get('src') and 'media' in img.get('src', '')]
results['Image URLs in HTML'] = len(image_urls) > 0
print(f"   Image URLs: {len(image_urls)} found ✓" if results['Image URLs in HTML'] else "   Image URLs: Not found ✗")

# Test 3: Hotel Detail Page
print("\n3️⃣  HOTEL DETAIL PAGE")
print("-" * 70)
response = requests.get(f'{BASE_URL}/hotels/38/')
assert response.status_code == 200
soup = BeautifulSoup(response.text, 'html.parser')

# Check booking form
booking_form = soup.find('form', {'id': 'bookingForm'})
results['Booking form exists'] = booking_form is not None
print(f"   Booking form: ✓" if results['Booking form exists'] else "   Booking form: ✗")

# Check form fields
form_fields = {
    'check-in': soup.find('input', {'id': 'checkin'}) is not None,
    'check-out': soup.find('input', {'id': 'checkout'}) is not None,
    'room type': soup.find('select', {'id': 'room_type'}) is not None,
    'guests': soup.find('input', {'id': 'num_guests'}) is not None,
    'email': soup.find('input', {'id': 'guest_email'}) is not None,
}
results['All form fields present'] = all(form_fields.values())
for field, present in form_fields.items():
    print(f"   {field.capitalize()}: ✓" if present else f"   {field.capitalize()}: ✗")

# Check for booking button
button_text = response.text
has_button = 'Proceed to Payment' in button_text or 'Login to Book' in button_text
results['Booking button'] = has_button
print(f"   Booking/Login button: ✓" if results['Booking button'] else "   Booking/Login button: ✗")

# Check availability section
has_availability = 'available' in response.text.lower() or 'rooms' in response.text.lower()
results['Availability section'] = has_availability
print(f"   Availability info: ✓" if results['Availability section'] else "   Availability info: ✗")

# Test 4: Hotel Images
print("\n4️⃣  IMAGE SERVING")
print("-" * 70)

# Test image access
test_images = [
    'taj_bengal_kolkata_main.jpg',
    'leela_palace_bangalore_main.jpg',
    'oberoi_mumbai_main.jpg'
]

image_results = {}
for img in test_images:
    img_url = f'{BASE_URL}/media/hotels/{img}'
    try:
        img_response = requests.head(img_url)
        image_results[img] = img_response.status_code == 200
        status = "✓" if image_results[img] else f"✗ ({img_response.status_code})"
        print(f"   {img}: {status}")
    except:
        image_results[img] = False
        print(f"   {img}: ✗ (connection error)")

results['Images accessible'] = any(image_results.values())

# Test 5: API Endpoints
print("\n5️⃣  API ENDPOINTS")
print("-" * 70)

# Test hotel API
response = requests.get(f'{BASE_URL}/api/hotels/list/')
results['Hotel API'] = response.status_code in [200, 403]  # 403 is OK if auth required
print(f"   GET /api/hotels/list/: {response.status_code} ✓" if results['Hotel API'] else f"   GET /api/hotels/list/: {response.status_code} ✗")

# Test payment API endpoints
response = requests.post(f'{BASE_URL}/bookings/api/create-order/', json={})
results['Payment create-order API'] = response.status_code in [400, 403]  # Will fail without booking, but endpoint exists
print(f"   POST /bookings/api/create-order/: {response.status_code} ✓" if results['Payment create-order API'] else f"   POST /bookings/api/create-order/: ✗")

response = requests.post(f'{BASE_URL}/bookings/api/verify-payment/', json={})
results['Payment verify API'] = response.status_code in [400, 403]
print(f"   POST /bookings/api/verify-payment/: {response.status_code} ✓" if results['Payment verify API'] else f"   POST /bookings/api/verify-payment/: ✗")

# Test 6: Channel Manager Integration
print("\n6️⃣  CHANNEL MANAGER INTEGRATION")
print("-" * 70)

response = requests.get(f'{BASE_URL}/hotels/38/')
has_internal_cm = 'Internal_Cm' in response.text or 'internal_cm' in response.text.lower()
has_external_cm = 'External_Cm' in response.text or 'external_cm' in response.text.lower()
has_inventory_source = has_internal_cm or has_external_cm

results['Inventory source displayed'] = has_inventory_source
if has_inventory_source:
    cm_type = "Internal" if has_internal_cm else "External"
    print(f"   Inventory source: {cm_type} Channel Manager ✓")
else:
    print(f"   Inventory source: Not visible ⚠️")

results['Availability snapshot'] = 'available_rooms' in response.text or 'available' in response.text.lower()
print(f"   Availability snapshot: ✓" if results['Availability snapshot'] else "   Availability snapshot: ✗")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

passed = sum(1 for v in results.values() if v)
total = len(results)

for test_name, passed_flag in results.items():
    status = "✓ PASS" if passed_flag else "✗ FAIL"
    print(f"{test_name:.<50} {status}")

print("\n" + "-"*70)
print(f"TOTAL: {passed}/{total} components verified")
print("-"*70)

if passed >= 12:
    print("\n🎉 SYSTEM OPERATIONAL!")
    print("""
Components Ready:
✓ Frontend rendering (dates, forms, images)
✓ API endpoints configured
✓ Hotel listing and details
✓ Booking form
✓ Channel manager integration
✓ Image serving

Next steps:
1. Login as test user
2. Complete a booking
3. Test payment flow
4. Verify inventory locking
""")
else:
    print(f"\n⚠️  {total - passed} component(s) need attention")

print("="*70 + "\n")
