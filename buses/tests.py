from django.test import TestCase, Client
from core.models import City
from buses.models import BusOperator, Bus, BusRoute, BusSchedule
from datetime import date, timedelta
from decimal import Decimal


class BusSearchTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.source = City.objects.create(name='Chennai', state='Tamil Nadu', code='MAA', is_popular=True)
        self.dest = City.objects.create(name='Mumbai', state='Maharashtra', code='MUM', is_popular=True)

        self.op = BusOperator.objects.create(name='Test Operator', contact_phone='9999999999')
        self.bus = Bus.objects.create(bus_number='TN01TEST', operator=self.op, total_seats=40)
        self.route = BusRoute.objects.create(
            bus=self.bus,
            source_city=self.source,
            destination_city=self.dest,
            route_name='CHN-MUM Express',
            departure_time='20:00',
            arrival_time='08:00',
            duration_hours=12.0,
            distance_km=500,
            base_fare=1200
        )

        base_date = date.today() + timedelta(days=1)
        for i in range(3):
            BusSchedule.objects.create(route=self.route, date=base_date + timedelta(days=i), available_seats=40, fare=1200, is_active=True)

    def test_search_by_ids(self):
        response = self.client.get(f'/buses/search/?source={self.source.id}&destination={self.dest.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # should return at least one route
        self.assertGreater(len(data.get('results', [])), 0)

    def test_search_by_names(self):
        # Legacy clients may pass names - ensure we handle this without raising
        response = self.client.get(f'/buses/search/?source={self.source.name}&destination={self.dest.name}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data.get('results', [])), 0)
