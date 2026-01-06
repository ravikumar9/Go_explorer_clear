from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, force_authenticate
from .models import Booking
from django.urls import reverse
import uuid


User = get_user_model()


class BookingE2ETests(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='pass')
        self.user = User.objects.create_user(username='user1', email='user1@example.com', password='pass')

        # Create a booking
        self.booking = Booking.objects.create(
            user=self.user,
            booking_type='hotel',
            status='confirmed',
            total_amount=1000,
            paid_amount=1000,
            customer_name='Test User',
            customer_email='test@example.com',
            customer_phone='9876543210'
        )

    def test_admin_booking_changelist_renders(self):
        logged = self.client.login(username='admin', password='pass')
        self.assertTrue(logged)
        url = reverse('admin:bookings_booking_changelist')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Ensure our booking id appears in the page
        self.assertIn(str(self.booking.booking_id)[:8].upper(), resp.content.decode())

    def test_booking_api_list_authenticated(self):
        # Force authenticate the API client as user
        self.api_client.force_authenticate(user=self.user)
        url = reverse('bookings:booking-list')
        resp = self.api_client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        # Should be a paginated response or list; check presence of our booking
        if isinstance(data, dict) and 'results' in data:
            results = data['results']
        else:
            results = data
        self.assertTrue(any(str(self.booking.booking_id) in (r.get('booking_id') or '') or r.get('customer_name')=='Test User' for r in results))
