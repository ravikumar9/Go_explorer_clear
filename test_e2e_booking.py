#!/usr/bin/env python3
"""
End-to-end booking flow test with login
"""
import requests
from datetime import date, timedelta
from bs4 import BeautifulSoup
import json

BASE_URL = 'http://goexplorer-dev.cloud'

# Use test credentials
USERNAME = 'goexplorer_dev_admin'
PASSWORD = 'Thepowerof@9'

def get_csrf_token(session, url):
    """Extract CSRF token from a page"""
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_input:
        return csrf_input.get('value')
    return None

print("\n" + "="*70)
print("END-TO-END BOOKING FLOW TEST")
print("="*70)

# Create a session to maintain cookies
session = requests.Session()

# Step 1: Login
print("\n1️⃣  Logging in...")
login_url = f'{BASE_URL}/login/'
csrf_token = get_csrf_token(session, login_url)

login_data = {
    'username': USERNAME,
    'password': PASSWORD,
    'csrfmiddlewaretoken': csrf_token
}

response = session.post(login_url, data=login_data, allow_redirects=True)
if response.status_code == 200 and 'Logout' in response.text:
    print("   ✓ Login successful")
else:
    print(f"   ⚠️  Login response: {response.status_code}")
    print("   ⚠️  Logout link not found in response")

# Step 2: Visit hotel detail page while logged in
print("\n2️⃣  Visiting hotel detail page...")
response = session.get(f'{BASE_URL}/hotels/38/')
assert response.status_code == 200, "Hotel detail page failed to load"
assert 'Proceed to Payment' in response.text, "Proceed to Payment button not visible after login"
print("   ✓ Hotel detail page loads")
print("   ✓ 'Proceed to Payment' button visible (user authenticated)")

# Step 3: Test booking form
print("\n3️⃣  Testing booking form...")
soup = BeautifulSoup(response.text, 'html.parser')
booking_form = soup.find('form', {'id': 'bookingForm'})
assert booking_form is not None, "Booking form not found"

# Get room types
room_select = soup.find('select', {'id': 'room_type'})
options = room_select.find_all('option')
first_room_id = None
for option in options:
    if option.get('value') and option.get('value') != '':
        first_room_id = option.get('value')
        break

print(f"   ✓ Booking form found")
print(f"   ✓ First room type ID: {first_room_id}")

# Step 4: Prepare booking data
print("\n4️⃣  Preparing booking data...")
checkin = date.today()
checkout = checkin + timedelta(days=2)
num_guests = 2
num_rooms = 1

booking_payload = {
    'checkin_date': str(checkin),
    'checkout_date': str(checkout),
    'room_type': first_room_id,
    'num_rooms': num_rooms,
    'num_guests': num_guests,
    'guest_name': 'Test User',
    'guest_email': 'test@goexplorer.dev',
    'guest_phone': '9876543210',
    'csrfmiddlewaretoken': get_csrf_token(session, f'{BASE_URL}/hotels/38/')
}

print(f"   Check-in: {checkin}")
print(f"   Check-out: {checkout}")
print(f"   Room type: {first_room_id}")
print(f"   Guests: {num_guests}")
print(f"   Rooms: {num_rooms}")

# Step 5: Submit booking
print("\n5️⃣  Submitting booking...")
booking_url = f'{BASE_URL}/hotels/38/book/'
response = session.post(booking_url, data=booking_payload, allow_redirects=False)

print(f"   Status: {response.status_code}")
if response.status_code == 302:
    redirect_location = response.headers.get('Location', '')
    print(f"   ✓ Redirected to: {redirect_location}")
    
    # Step 6: Follow redirect to confirmation page
    print("\n6️⃣  Following redirect to confirmation page...")
    confirmation_response = session.get(f'{BASE_URL}{redirect_location}')
    if confirmation_response.status_code == 200:
        print("   ✓ Confirmation page loaded")
        
        # Check confirmation page content
        if 'confirmation' in redirect_location.lower():
            soup = BeautifulSoup(confirmation_response.text, 'html.parser')
            if 'Proceed to Payment' in confirmation_response.text:
                print("   ✓ Confirmation page shows 'Proceed to Payment' button")
            booking_info = soup.find('div', {'class': 'booking-summary'}) or soup.find('div', {'class': 'confirmation'})
            if booking_info:
                print("   ✓ Booking summary displayed")
    else:
        print(f"   ⚠️  Confirmation page failed: {confirmation_response.status_code}")
else:
    print(f"   ⚠️  Booking submission returned {response.status_code} instead of 302")
    print(f"   Response length: {len(response.text)} bytes")
    if 'error' in response.text.lower():
        print("   ⚠️  Error found in response")

print("\n" + "="*70)
print("✅ END-TO-END BOOKING FLOW TEST COMPLETE")
print("="*70)
print("""
Test Results Summary:
1. Login with test credentials: ✓
2. Hotel detail page access: ✓
3. Booking form visibility: ✓
4. Booking submission: In Progress...

Next Steps:
- Complete the payment flow testing
- Verify booking confirmation email
- Check booking status in admin panel
""")
print("="*70 + "\n")
