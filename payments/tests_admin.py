from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from bookings.models import Booking
from .models import Payment


class PaymentAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(username='admin2', email='admin2@example.com', password='pass')
        self.staff = User.objects.create_user(username='staff', email='staff@example.com', password='pass', is_staff=True)

        self.booking = Booking.objects.create(
            user=self.superuser,
            booking_type='bus',
            status='pending',
            total_amount=200.00,
            paid_amount=0.00,
            customer_name='Pay User',
            customer_email='pay@example.com',
            customer_phone='8888888888'
        )

        self.payment = Payment.objects.create(
            booking=self.booking,
            amount=200.00,
            currency='INR',
            payment_method='razorpay',
            status='success'
        )

    def test_export_payments_csv_as_superuser(self):
        client = Client()
        client.login(username='admin2', password='pass')
        url = reverse('admin:payments_payment_changelist')
        data = {'action': 'export_as_csv', '_selected_action': [str(self.payment.pk)]}
        resp = client.post(url, data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv')
