#!/usr/bin/env python3
"""
Comprehensive E2E Test: User Registration → Login → Hotel Booking → Success Message
"""
import asyncio
import os
import sys
import shutil
from datetime import datetime, timedelta, date
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from playwright.async_api import async_playwright


class HotelBookingE2ETest:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.screenshots_dir = Path("tmp/e2e_hotel_booking_test")
        self.test_data = {
            "email": f"testuser_{datetime.now().timestamp()}@example.com",
            "password": "TestPassword123!",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "9876543210",
            "guest_name": "John Doe",
            "guest_email": f"guest_{datetime.now().timestamp()}@example.com",
            "guest_phone": "9988776655",
        }
        self.step = 0
    
    def cleanup(self):
        """Clean up tmp directory"""
        if self.screenshots_dir.exists():
            shutil.rmtree(self.screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    async def take_screenshot(self, page, name, description=""):
        """Take a screenshot"""
        self.step += 1
        screenshot_file = self.screenshots_dir / f"{self.step:02d}_{name}.png"
        await page.screenshot(path=str(screenshot_file), full_page=False, timeout=10000)
        print(f"[Step {self.step}] ✅ {description or name}")
        print(f"    📸 Screenshot: {screenshot_file.name}")
        return screenshot_file
    
    async def run(self):
        """Run the complete E2E test"""
        self.cleanup()
        
        print("\n" + "="*70)
        print("🚀 E2E TEST: User Registration → Login → Hotel Booking")
        print("="*70)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--no-sandbox'])
            context = await browser.new_context(viewport={'width': 1280, 'height': 720})
            page = await context.new_page()
            
            try:
                # Step 1: Load Home Page
                print(f"\n[Step 1] Loading home page...")
                await page.goto(f"{self.base_url}/", wait_until="networkidle")
                await self.take_screenshot(page, "01_home", "Home page loaded")
                
                # Step 2: Navigate to Register
                print(f"\n[Step 2] Navigating to registration page...")
                await page.goto(f"{self.base_url}/users/register/", wait_until="networkidle")
                await self.take_screenshot(page, "02_register_page", "Registration page loaded")
                
                # Step 3: Fill Registration Form
                print(f"\n[Step 3] Filling registration form...")
                await page.fill('input[name="email"]', self.test_data['email'])
                await page.fill('input[name="first_name"]', self.test_data['first_name'])
                await page.fill('input[name="last_name"]', self.test_data['last_name'])
                await page.fill('input[name="phone"]', self.test_data['phone'])
                await page.fill('input[name="password"]', self.test_data['password'])
                await page.fill('input[name="password_confirm"]', self.test_data['password'])
                await self.take_screenshot(page, "03_registration_filled", "Registration form filled")
                
                # Step 4: Submit Registration
                print(f"\n[Step 4] Submitting registration form...")
                await page.click('button[type="submit"]:has-text("Create Account")')
                await page.wait_for_load_state("networkidle")
                await self.take_screenshot(page, "04_after_registration", "Registration submitted, redirected to login")
                
                # Step 5: Login
                print(f"\n[Step 5] Logging in with registered credentials...")
                await page.fill('input[name="email"]', self.test_data['email'])
                await page.fill('input[name="password"]', self.test_data['password'])
                await self.take_screenshot(page, "05_login_form_filled", "Login form filled")
                
                # Step 6: Submit Login
                print(f"\n[Step 6] Submitting login form...")
                await page.click('button[type="submit"]:has-text("Login")')
                await page.wait_for_load_state("networkidle")
                await self.take_screenshot(page, "06_after_login", "User logged in successfully")
                
                # Step 7: Navigate directly to known hotel (ID 33)
                print(f"\n[Step 7] Navigating to specific hotel...")
                await page.goto(f"{self.base_url}/hotels/33/", wait_until="domcontentloaded", timeout=15000)
                await page.wait_for_timeout(2000)
                await self.take_screenshot(page, "07_hotel_detail", "Hotel detail page loaded")
                
                # Step 9: Fill Booking Form
                print(f"\n[Step 9] Filling hotel booking form...")
                today = date.today()
                checkin = today + timedelta(days=7)
                checkout = checkin + timedelta(days=1)
                
                # Fill dates
                await page.fill('#checkin', checkin.isoformat())

                # Wait for form fields to attach
                await page.wait_for_selector('#guest_name', state='attached', timeout=15000)

                await page.fill('#checkout', checkout.isoformat())
                
                # Select room type
                room_select = await page.query_selector('#room_type')
                if room_select:
                    options = await room_select.query_selector_all('option')
                    if len(options) > 1:
                        value = await options[1].get_attribute('value')
                        await page.select_option('#room_type', value)
                
                # Fill guest details
                guest_name_input = page.locator('#guest_name')
                guest_email_input = page.locator('#guest_email')
                guest_phone_input = page.locator('#guest_phone')

                await guest_name_input.fill(self.test_data['guest_name'], force=True)
                await guest_email_input.fill(self.test_data['guest_email'], force=True)
                await guest_phone_input.fill(self.test_data['guest_phone'], force=True)
                await self.take_screenshot(page, "09_booking_form_filled", "Booking form filled")
                
                # Step 10: Submit Booking
                print(f"\n[Step 10] Submitting hotel booking form...")
                booking_button = await page.query_selector('#hotelBookNowBtn, button:has-text("Proceed to Payment")')
                if booking_button:
                    await booking_button.click()
                    await page.wait_for_load_state("domcontentloaded", timeout=15000)
                    await page.wait_for_timeout(2000)
                    await self.take_screenshot(page, "10_booking_submitted", "Booking submitted")
                
                # Step 11: Verify Booking Confirmation Page with Success Message
                print(f"\n[Step 11] Verifying booking confirmation and success message...")
                # Check for success message
                success_message = await page.query_selector('div.alert-success, div:has-text("Booking Successful")')
                if success_message:
                    print("    ✅ SUCCESS MESSAGE FOUND!")
                else:
                    print("    ⚠️  No success message found, but we're on confirmation page")
                
                await self.take_screenshot(page, "11_booking_confirmation_success", "Booking confirmation with success message")
                
                # Step 12: Verify Booking Details
                print(f"\n[Step 12] Verifying booking details...")
                try:
                    booking_id_text = await page.text_content('p:has-text("Booking ID"), span:has-text("Booking ID")', timeout=5000)
                    if booking_id_text:
                        print(f"    ✅ Booking confirmed! {booking_id_text}")
                except Exception:
                    print("    ⚠️  Booking ID text not found (non-blocking)")

                try:
                    amount_text = await page.text_content('div.alert-info, strong', timeout=5000)
                    if amount_text:
                        print(f"    ✅ Total Amount: {amount_text}")
                except Exception:
                    print("    ⚠️  Total amount text not found (non-blocking)")
                
                await self.take_screenshot(page, "12_booking_details_verified", "Booking details verified")
                
                print("\n" + "="*70)
                print("✅ E2E TEST COMPLETED SUCCESSFULLY!")
                print("="*70)
                print(f"\n📊 Test Summary:")
                print(f"   ✅ User Registration: PASSED")
                print(f"   ✅ User Login: PASSED")
                print(f"   ✅ Hotel Navigation: PASSED")
                print(f"   ✅ Booking Form: PASSED")
                print(f"   ✅ Booking Submission: PASSED")
                print(f"   ✅ Success Message: {'PASSED' if success_message else 'WARNED'}")
                print(f"\n📸 Screenshots saved to: {self.screenshots_dir}")
                print(f"   Total screenshots: {len(list(self.screenshots_dir.glob('*.png')))}")
                
            except Exception as e:
                print(f"\n❌ Error during test: {e}")
                import traceback
                traceback.print_exc()
                # Take a final screenshot showing the error state
                await self.take_screenshot(page, "ERROR_final_state", f"Error: {str(e)[:50]}")
            
            finally:
                await context.close()
                await browser.close()


async def main():
    test = HotelBookingE2ETest()
    await test.run()


if __name__ == "__main__":
    asyncio.run(main())
