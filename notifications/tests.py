"""
Comprehensive notification tests
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from notifications.models import (
    NotificationTemplate, Notification, NotificationPreference
)
from notifications.services import (
    EmailService, WhatsAppService, SMSService, NotificationManager
)
from notifications.whatsapp import WhatsAppBookingHandler, TEST_WHATSAPP_MESSAGES

User = get_user_model()


class NotificationTemplateTest(TestCase):
    """Test notification templates"""
    
    def setUp(self):
        self.template = NotificationTemplate.objects.create(
            name='booking_confirmation',
            notification_type='email',
            subject='Your Booking - {booking_id}',
            body='Booking ID: {booking_id}\nHotel: {property_name}',
            is_active=True
        )
    
    def test_template_creation(self):
        """Test creating notification template"""
        self.assertIsNotNone(self.template.id)
        self.assertEqual(self.template.name, 'booking_confirmation')
        self.assertEqual(self.template.notification_type, 'email')
    
    def test_template_string(self):
        """Test template string representation"""
        self.assertIn('Booking Confirmation', str(self.template))
        self.assertIn('Email', str(self.template))


class NotificationPreferenceTest(TestCase):
    """Test notification preferences"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.preference = NotificationPreference.objects.create(
            user=self.user,
            email_booking_confirmation=True,
            whatsapp_number='+919876543210',
            phone_number='+919876543210'
        )
    
    def test_preference_creation(self):
        """Test creating user preferences"""
        self.assertEqual(self.preference.user, self.user)
        self.assertTrue(self.preference.email_booking_confirmation)
        self.assertEqual(self.preference.whatsapp_number, '+919876543210')
    
    def test_user_preference_relationship(self):
        """Test user-preference relationship"""
        user_pref = self.user.notification_preference
        self.assertEqual(user_pref.whatsapp_number, '+919876543210')


class NotificationTest(TestCase):
    """Test notification tracking"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.notification = Notification.objects.create(
            user=self.user,
            notification_type='email',
            recipient='test@example.com',
            subject='Test Email',
            body='This is a test email',
            status='sent'
        )
    
    def test_notification_creation(self):
        """Test creating notification record"""
        self.assertEqual(self.notification.user, self.user)
        self.assertEqual(self.notification.status, 'sent')
    
    def test_mark_sent(self):
        """Test marking notification as sent"""
        notif = Notification.objects.create(
            user=self.user,
            notification_type='email',
            recipient='test@example.com',
            body='Test',
            status='pending'
        )
        
        notif.mark_sent('ref-123')
        notif.refresh_from_db()
        
        self.assertEqual(notif.status, 'sent')
        self.assertEqual(notif.provider_reference, 'ref-123')
        self.assertIsNotNone(notif.sent_at)
    
    def test_mark_failed(self):
        """Test marking notification as failed"""
        notif = Notification.objects.create(
            user=self.user,
            notification_type='email',
            recipient='test@example.com',
            body='Test',
            status='pending'
        )
        
        notif.mark_failed('Invalid email address')
        notif.refresh_from_db()
        
        self.assertEqual(notif.status, 'failed')
        self.assertIn('Invalid email', notif.error_message)


class EmailServiceTest(TestCase):
    """Test email notification service"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test'
        )
    
    def test_send_email(self):
        """Test sending email"""
        result = EmailService.send_email(
            self.user,
            subject='Test Subject',
            body='Test body'
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.recipient, 'test@example.com')


class WhatsAppServiceTest(TestCase):
    """Test WhatsApp notification service"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.pref = NotificationPreference.objects.create(
            user=self.user,
            whatsapp_number='+919876543210'
        )
    
    def test_send_whatsapp_message(self):
        """Test sending WhatsApp message"""
        result = WhatsAppService.send_message(
            self.user,
            '+919876543210',
            'test_template'
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.recipient, '+919876543210')


class SMSServiceTest(TestCase):
    """Test SMS notification service"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.pref = NotificationPreference.objects.create(
            user=self.user,
            phone_number='+919876543210'
        )
    
    def test_send_sms(self):
        """Test sending SMS"""
        result = SMSService.send_sms(
            self.user,
            '+919876543210',
            'Your booking is confirmed!'
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result.recipient, '+919876543210')


class NotificationManagerTest(TestCase):
    """Test unified notification manager"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        NotificationPreference.objects.create(
            user=self.user,
            email_booking_confirmation=True,
            whatsapp_booking_confirmation=True,
            whatsapp_number='+919876543210'
        )
    
    def test_send_booking_confirmation(self):
        """Test sending all booking confirmation notifications"""
        booking_data = {
            'booking_id': 'BK-001',
            'property_name': 'Test Hotel',
            'booking_date': '2026-01-15',
            'booking_type': 'Hotel',
            'price': '5000'
        }
        
        results = NotificationManager.send_booking_confirmation(
            self.user,
            booking_data
        )
        
        self.assertIn('email', results)
        self.assertIn('whatsapp', results)


class WhatsAppBookingHandlerTest(TestCase):
    """Test WhatsApp booking handler"""
    
    def test_search_hotels(self):
        """Test searching for hotels via WhatsApp"""
        response = WhatsAppBookingHandler.process_message(
            '+919876543210',
            '/search hotels bangalore'
        )
        
        self.assertTrue(response['success'])
        self.assertIn('Hotels', response['message'])
    
    def test_search_buses(self):
        """Test searching for buses"""
        response = WhatsAppBookingHandler.process_message(
            '+919876543210',
            '/search buses bangalore hyderabad'
        )
        
        self.assertTrue(response['success'])
        self.assertIn('Buses', response['message'])
    
    def test_search_packages(self):
        """Test searching for packages"""
        response = WhatsAppBookingHandler.process_message(
            '+919876543210',
            '/search packages goa'
        )
        
        self.assertTrue(response['success'])
        self.assertIn('Packages', response['message'])
    
    def test_booking_request(self):
        """Test booking via WhatsApp"""
        response = WhatsAppBookingHandler.process_message(
            '+919876543210',
            '/book hotel 1 2026-01-15 1'
        )
        
        self.assertTrue(response['success'])
        self.assertIn('Booking ID', response['message'])
        self.assertIn('WA-', response['booking_id'])
    
    def test_check_status(self):
        """Test checking booking status"""
        response = WhatsAppBookingHandler.process_message(
            '+919876543210',
            '/status WA-20260102120000-1'
        )
        
        self.assertTrue(response['success'])
        self.assertIn('Status', response['message'])
    
    def test_cancel_booking(self):
        """Test cancelling booking"""
        response = WhatsAppBookingHandler.process_message(
            '+919876543210',
            '/cancel WA-20260102120000-1'
        )
        
        self.assertTrue(response['success'])
        self.assertIn('Cancellation', response['message'])
    
    def test_help_command(self):
        """Test help command"""
        response = WhatsAppBookingHandler.process_message(
            '+919876543210',
            '/help'
        )
        
        self.assertTrue(response['success'])
        self.assertIn('Commands', response['message'])
    
    def test_unknown_command(self):
        """Test unknown command"""
        response = WhatsAppBookingHandler.process_message(
            '+919876543210',
            'What is 2+2?'
        )
        
        self.assertFalse(response['success'])
        self.assertIn("didn't understand", response['message'])
    
    def test_all_test_messages(self):
        """Test all predefined test messages"""
        for command, message in TEST_WHATSAPP_MESSAGES.items():
            response = WhatsAppBookingHandler.process_message(
                '+919876543210',
                message
            )
            
            self.assertIsNotNone(response)
            self.assertIn('message', response)
            # Clean response message of any unicode characters for stdout
            msg_text = response['message'][:50] if 'message' in response else 'N/A'
            try:
                msg_text = msg_text.encode('ascii', 'ignore').decode('ascii')
            except:
                msg_text = 'N/A'
            # Don't print in tests to avoid encoding issues
            # print(f"[+] {command}: {msg_text}...")
