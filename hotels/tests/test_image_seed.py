from django.test import TestCase
from django.core.management import call_command
from unittest.mock import patch
from core.models import City
from hotels.models import Hotel

class HotelImageSeedTests(TestCase):
    def setUp(self):
        self.city = City.objects.create(name='Mumbai', state='Maharashtra')
        Hotel.objects.create(name='Taj Mahal Palace', description='desc', city=self.city, address='addr', contact_phone='123', contact_email='a@b.com')

    @patch('requests.get')
    def test_add_hotel_images_uses_placeholder_on_download_failure(self, mock_get):
        # simulate network failure
        mock_get.side_effect = Exception('network')
        call_command('add_hotel_images')
        hotel = Hotel.objects.get(name='Taj Mahal Palace')
        # After command, hotel.image should be set from local placeholder
        self.assertTrue(hotel.image, 'Hotel image should be set (placeholder)')
