from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Booking
from django.utils import timezone


class BookingAdminActionsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(username='admin', email='admin@example.com', password='pass')
        self.client = Client()
        self.client.login(username='admin', password='pass')

        # create a booking
        self.booking = Booking.objects.create(
            user=self.admin_user,
            booking_type='hotel',
            status='pending',
            total_amount=100.00,
            paid_amount=0.00,
            customer_name='Test User',
            customer_email='test@example.com',
            customer_phone='9999999999'
        )

    def test_export_bookings_action(self):
        url = reverse('admin:bookings_booking_changelist')
        data = {
            'action': 'export_as_csv',
            '_selected_action': [str(self.booking.pk)],
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_soft_delete_action(self):
        url = reverse('admin:bookings_booking_changelist')
        data = {
            'action': 'soft_delete_action',
            '_selected_action': [str(self.booking.pk)],
        }
        response = self.client.post(url, data, follow=True)
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.is_deleted)
