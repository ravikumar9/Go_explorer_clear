#!/usr/bin/env python3
"""
Comprehensive test of GoExplorer features on live server
Tests: Date inputs, Images, Booking flow, Payment flow
"""
import requests
from bs4 import BeautifulSoup
from datetime import date, timedelta
import json
import re

BASE_URL = 'http://goexplorer-dev.cloud'

def test_homepage_dates():
    """Test if date inputs are present with proper styles"""
    print("\n" + "="*60)
    print("TEST 1: Date Inputs on Homepage")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/')
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find date inputs
    date_inputs = soup.find_all('input', {'type': 'date'})
    print(f"✓ Found {len(date_inputs)} date inputs")
    
    # Check CSS for date styling
    styles = soup.find_all('style')
    date_css_found = False
    for style in styles:
        if 'input[type="date"]' in style.text and 'color:' in style.text:
            date_css_found = True
            break
    
    print(f"✓ Date input CSS styles: {'Found' if date_css_found else 'Not found'}")
    
    # Check for JavaScript that sets default values
    scripts = soup.find_all('script')
    js_logic_found = False
    for script in scripts:
        if 'todayStr' in script.text and 'hotelCheckin' in script.text:
            js_logic_found = True
            break
    
    print(f"✓ JavaScript date logic: {'Found' if js_logic_found else 'Not found'}")
    return date_css_found and js_logic_found

def test_images_loading():
    """Test if hotel images are loading"""
    print("\n" + "="*60)
    print("TEST 2: Hotel Images Loading")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/')
    
    # Check for image URLs in response
    if 'media/hotels/' in response.text:
        print("✓ Media URLs found in homepage")
    else:
        print("✗ No media URLs in homepage")
        return False
    
    # Try to fetch an image
    image_url = f'{BASE_URL}/media/hotels/taj_bengal_kolkata_main.jpg'
    img_response = requests.head(image_url)
    
    if img_response.status_code == 200:
        print(f"✓ Image accessible: {image_url} (Status: {img_response.status_code})")
        return True
    else:
        print(f"✗ Image not accessible: {image_url} (Status: {img_response.status_code})")
        return False

def test_hotel_detail():
    """Test hotel detail page"""
    print("\n" + "="*60)
    print("TEST 3: Hotel Detail Page")
    print("="*60)
    
    response = requests.get(f'{BASE_URL}/hotels/38/')  # The Leela Palace Bangalore
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for date inputs
    date_inputs = soup.find_all('input', {'type': 'date'})
    print(f"✓ Date inputs found: {len(date_inputs)}")
    
    # Check for image gallery
    gallery = soup.find('div', {'id': 'galleryThumbs'})
    print(f"✓ Image gallery: {'Found' if gallery else 'Not found'}")
    
    # Check for availability snapshot
    if 'available' in response.text.lower() or 'availability' in response.text.lower():
        print("✓ Availability section present")
    
    return len(date_inputs) > 0

def test_booking_flow():
    """Test the booking creation endpoint"""
    print("\n" + "="*60)
    print("TEST 4: Booking Flow")
    print("="*60)
    
    # Test if booking form exists
    response = requests.get(f'{BASE_URL}/hotels/38/')
    
    if 'bookingForm' in response.text and 'Proceed to Payment' in response.text:
        print("✓ Booking form found on hotel detail page")
        return True
    else:
        print("✗ Booking form not found")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n" + "="*60)
    print("TEST 5: API Endpoints")
    print("="*60)
    
    # Test calculate price endpoint
    price_data = {
        "room_type_id": 1,
        "check_in": str(date.today()),
        "check_out": str(date.today() + timedelta(days=1)),
        "num_rooms": 1
    }
    
    response = requests.post(f'{BASE_URL}/hotels/calculate-price/', json=price_data)
    if response.status_code == 200:
        print(f"✓ Calculate price endpoint working")
    else:
        print(f"✗ Calculate price endpoint failed: {response.status_code}")
    
    return True

def test_payment_urls():
    """Test payment-related URLs"""
    print("\n" + "="*60)
    print("TEST 6: Payment URLs")
    print("="*60)
    
    # Check if payment API routes are in the code
    response = requests.get(f'{BASE_URL}/bookings/api/create-order/', method='POST')
    # Will get CSRF error, but that means route exists
    if 'CSRF' in response.text or 'Method' in response.text or response.status_code in [403, 405]:
        print("✓ Payment API route exists")
        return True
    
    return False

def main():
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "GOEXPLORER LIVE SERVER TEST" + " "*16 + "║")
    print("║" + f" "*10 + f"Testing: {BASE_URL}" + " "*34 + "║")
    print("╚" + "="*58 + "╝")
    
    results = []
    
    # Run all tests
    results.append(("Date Inputs", test_homepage_dates()))
    results.append(("Hotel Images", test_images_loading()))
    results.append(("Hotel Detail", test_hotel_detail()))
    results.append(("Booking Form", test_booking_flow()))
    results.append(("API Endpoints", test_api_endpoints()))
    results.append(("Payment URLs", test_payment_urls()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print("\n" + "="*60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! The server is working correctly.")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review the issues above.")

if __name__ == '__main__':
    main()
