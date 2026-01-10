from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from core.models import TimeStampedModel, City
from datetime import date


class BusOperator(TimeStampedModel):
    """Bus operator/company"""
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='buses/operators/', null=True, blank=True)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # Registration & Verification
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='bus_operator_profile')
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_operators')
    
    # Business Details
    business_license = models.CharField(max_length=100, blank=True)
    pan_number = models.CharField(max_length=20, blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    registered_address = models.TextField(blank=True)
    
    # Stats
    total_trips_completed = models.IntegerField(default=0)
    total_bookings = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-rating', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_verification_status_display()})"


class Bus(TimeStampedModel):
    """Bus model"""
    BUS_TYPES = [
        ('seater', 'Seater'),
        ('sleeper', 'Sleeper'),
        ('semi_sleeper', 'Semi-Sleeper'),
        ('ac_seater', 'AC Seater'),
        ('ac_sleeper', 'AC Sleeper'),
        ('volvo', 'Volvo'),
        ('luxury', 'Luxury'),
    ]
    
    operator = models.ForeignKey(BusOperator, on_delete=models.CASCADE, related_name='buses')
    bus_number = models.CharField(max_length=50, unique=True)
    bus_name = models.CharField(max_length=200)
    bus_type = models.CharField(max_length=20, choices=BUS_TYPES)
    
    total_seats = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Bus Details (Industry Standard)
    manufacturing_year = models.IntegerField(null=True, blank=True, help_text="Year of manufacturing")
    registration_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    chassis_number = models.CharField(max_length=100, blank=True)
    
    # Amenities
    has_ac = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=False)
    has_charging_point = models.BooleanField(default=False)
    has_blanket = models.BooleanField(default=False)
    has_water_bottle = models.BooleanField(default=False)
    has_tv = models.BooleanField(default=False)
    has_reading_light = models.BooleanField(default=False)
    has_emergency_exit = models.BooleanField(default=True)
    has_first_aid = models.BooleanField(default=True)
    has_gps_tracking = models.BooleanField(default=False)
    has_cctv = models.BooleanField(default=False)
    
    # Ratings & Reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    total_reviews = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['operator', 'bus_number']
    
    def __str__(self):
        return f"{self.operator.name} - {self.bus_number}"
    
    @property
    def bus_age(self):
        """Calculate bus age in years"""
        if self.manufacturing_year:
            return date.today().year - self.manufacturing_year
        return None
    
    def get_amenities_list(self):
        """Get list of amenities"""
        amenities = []
        if self.has_ac: amenities.append('AC')
        if self.has_wifi: amenities.append('WiFi')
        if self.has_charging_point: amenities.append('Charging Point')
        if self.has_blanket: amenities.append('Blanket')
        if self.has_water_bottle: amenities.append('Water Bottle')
        if self.has_tv: amenities.append('TV')
        if self.has_reading_light: amenities.append('Reading Light')
        if self.has_emergency_exit: amenities.append('Emergency Exit')
        if self.has_first_aid: amenities.append('First Aid')
        if self.has_gps_tracking: amenities.append('GPS Tracking')
        if self.has_cctv: amenities.append('CCTV')
        return amenities


class BusRoute(TimeStampedModel):
    """Bus route between cities"""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='routes')
    route_name = models.CharField(max_length=200)
    
    source_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='bus_routes_from')
    destination_city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='bus_routes_to')
    
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2)
    distance_km = models.DecimalField(max_digits=7, decimal_places=2)
    
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_active = models.BooleanField(default=True)
    
    # Days of operation
    operates_monday = models.BooleanField(default=True)
    operates_tuesday = models.BooleanField(default=True)
    operates_wednesday = models.BooleanField(default=True)
    operates_thursday = models.BooleanField(default=True)
    operates_friday = models.BooleanField(default=True)
    operates_saturday = models.BooleanField(default=True)
    operates_sunday = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['source_city', 'destination_city', 'departure_time']
    
    def __str__(self):
        return f"{self.source_city.name} to {self.destination_city.name} - {self.departure_time}"
    
    def get_available_seats(self, date):
        """Get available seats for a specific date"""
        schedule = self.schedules.filter(date=date, is_active=True).first()
        if schedule:
            return schedule.available_seats
        return self.bus.total_seats
    
    def calculate_fare(self, num_seats, convenience_fee_pct=2.0, gst_pct=5.0):
        """
        Calculate total fare for given number of seats
        
        Args:
            num_seats: Number of seats to book
            convenience_fee_pct: Convenience fee percentage (default 2%)
            gst_pct: GST percentage (default 5%)
        
        Returns:
            dict with base, fee, gst, total amounts
        """
        from decimal import Decimal
        
        base_fare = Decimal(str(self.base_fare)) * Decimal(str(num_seats))
        conv_fee = base_fare * Decimal(str(convenience_fee_pct)) / Decimal('100')
        gst = (base_fare + conv_fee) * Decimal(str(gst_pct)) / Decimal('100')
        total = base_fare + conv_fee + gst
        
        return {
            'base_fare': float(base_fare),
            'convenience_fee': float(conv_fee),
            'gst': float(gst),
            'total': float(total),
            'num_seats': num_seats,
            'per_seat': float(self.base_fare),
        }


class BoardingPoint(models.Model):
    """Boarding points for bus routes (RedBus/AbhiBus style)"""
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='boarding_points')
    name = models.CharField(max_length=200, help_text="e.g., Majestic Bus Stand, Electronic City")
    address = models.TextField()
    landmark = models.CharField(max_length=200, blank=True, help_text="Nearby landmark")
    
    # Location
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    pincode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Timing
    pickup_time = models.TimeField(help_text="Pickup time at this point")
    
    # Contact
    contact_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Display order
    sequence_order = models.IntegerField(default=1, help_text="Order of pickup points")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['route', 'sequence_order', 'pickup_time']
        unique_together = ['route', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.pickup_time.strftime('%H:%M')}"


class DroppingPoint(models.Model):
    """Dropping points for bus routes (RedBus/AbhiBus style)"""
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='dropping_points')
    name = models.CharField(max_length=200, help_text="e.g., Koyambedu, CMBT")
    address = models.TextField()
    landmark = models.CharField(max_length=200, blank=True, help_text="Nearby landmark")
    
    # Location
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    pincode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Timing
    drop_time = models.TimeField(help_text="Drop time at this point")
    
    # Contact
    contact_person = models.CharField(max_length=100, blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    # Display order
    sequence_order = models.IntegerField(default=1, help_text="Order of drop points")
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['route', 'sequence_order', 'drop_time']
        unique_together = ['route', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.drop_time.strftime('%H:%M')}"


class BusStop(models.Model):
    """Intermediate stops for a bus route"""
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='stops')
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    stop_name = models.CharField(max_length=200)
    stop_order = models.IntegerField()
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    
    class Meta:
        ordering = ['route', 'stop_order']
        unique_together = ['route', 'stop_order']
    
    def __str__(self):
        return f"{self.route} - {self.stop_name}"


class BusSchedule(TimeStampedModel):
    """Bus schedule for specific dates - tracks daily availability"""
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    available_seats = models.IntegerField(help_text="Seats currently available")
    booked_seats = models.IntegerField(default=0, help_text="Seats already booked")
    
    fare = models.DecimalField(max_digits=10, decimal_places=2, help_text="Dynamic pricing per seat")
    
    # Status tracking
    is_active = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    cancellation_reason = models.TextField(blank=True)
    
    # Window seat pricing (premium)
    window_seat_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ['route', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.route} - {self.date} ({self.available_seats} seats left)"
    
    def book_seats(self, num_seats):
        """Book seats and update availability"""
        if self.available_seats >= num_seats:
            self.available_seats -= num_seats
            self.booked_seats += num_seats
            self.save()
            return True
        return False
    
    @property
    def occupancy_percentage(self):
        """Calculate occupancy percentage"""
        total = self.available_seats + self.booked_seats
        if total > 0:
            return round((self.booked_seats / total) * 100, 1)
        return 0
    
    @property
    def is_almost_full(self):
        """Check if bus is almost full (>80% booked)"""
        return self.occupancy_percentage > 80


class SeatLayout(models.Model):
    """Seat layout for buses"""
    SEAT_TYPES = [
        ('seater', 'Seater'),
        ('sleeper_lower', 'Sleeper Lower'),
        ('sleeper_upper', 'Sleeper Upper'),
    ]
    
    RESERVED_FOR_CHOICES = [
        ('general', 'General'),
        ('ladies', 'Ladies Only'),
        ('disabled', 'Disabled'),
    ]
    
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seat_layout')
    seat_number = models.CharField(max_length=10)
    seat_type = models.CharField(max_length=20, choices=SEAT_TYPES)
    row = models.IntegerField()
    column = models.IntegerField()
    deck = models.IntegerField(default=1)  # 1 for lower deck, 2 for upper deck
    
    # Ladies seat reservation
    reserved_for = models.CharField(max_length=20, choices=RESERVED_FOR_CHOICES, default='general', 
                                     help_text="Reserve seats for specific passenger types")
    
    class Meta:
        unique_together = ['bus', 'seat_number']
        ordering = ['deck', 'row', 'column']
    
    def __str__(self):
        return f"{self.bus.bus_number} - Seat {self.seat_number} ({self.get_reserved_for_display()})"
    
    def can_be_booked_by(self, passenger_gender):
        """Check if seat can be booked by passenger gender"""
        if self.reserved_for == 'general':
            return True
        elif self.reserved_for == 'ladies':
            return passenger_gender == 'F'  # Only females can book ladies seats
        elif self.reserved_for == 'disabled':
            return True  # Disabled passengers can book disabled seats
        return False
