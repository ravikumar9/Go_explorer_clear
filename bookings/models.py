from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel
from hotels.models import Hotel, RoomType
from buses.models import BusSchedule, SeatLayout, BusRoute
from packages.models import PackageDeparture
import uuid
import json


class Booking(TimeStampedModel):
    """Base booking model"""
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('deleted', 'Deleted'),
    ]
    
    BOOKING_TYPES = [
        ('hotel', 'Hotel'),
        ('bus', 'Bus'),
        ('package', 'Package'),
    ]

    INVENTORY_CHANNELS = [
        ('internal_cm', 'Internal CM'),
        ('external_cm', 'External CM'),
    ]
    
    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    
    # Channel / External integration fields
    external_booking_id = models.CharField(max_length=200, null=True, blank=True, db_index=True)
    channel_name = models.CharField(max_length=100, null=True, blank=True)
    channel_reference = models.CharField(max_length=200, null=True, blank=True)
    sync_status = models.CharField(max_length=50, default='pending', choices=[('pending','Pending'), ('synced','Synced'), ('failed','Failed')])
    last_synced_at = models.DateTimeField(null=True, blank=True)
    booking_source = models.CharField(max_length=20, choices=[('internal','Internal'), ('external','External')], default='internal')
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPES)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')

    inventory_channel = models.CharField(max_length=20, choices=INVENTORY_CHANNELS, default='internal_cm')
    lock_id = models.CharField(max_length=128, blank=True)
    cm_booking_id = models.CharField(max_length=128, blank=True)
    payment_reference = models.CharField(max_length=128, blank=True)
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Contact details
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15)
    
    # NOTE: PII should be encrypted in the DB in production. For now we provide mask helpers.
    def masked_phone(self):
        if not self.customer_phone:
            return ''
        s = str(self.customer_phone)
        if len(s) <= 4:
            return '****'
        return s[:2] + '*' * (len(s) - 4) + s[-2:]

    def masked_email(self):
        if not self.customer_email:
            return ''
        parts = self.customer_email.split('@')
        if len(parts[0]) <= 2:
            local = '*' * len(parts[0])
        else:
            local = parts[0][0] + '*' * (len(parts[0]) - 2) + parts[0][-1]
        return f"{local}@{parts[1]}"
    
    special_requests = models.TextField(blank=True)
    
    # Cancellation
    cancellation_reason = models.TextField(blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Soft delete tracking
    is_deleted = models.BooleanField(default=False)
    deleted_reason = models.TextField(blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_bookings')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.booking_id} - {self.user.username} - {self.booking_type}"
    
    def soft_delete(self, user=None, reason=''):
        """Soft delete booking"""
        self.is_deleted = True
        self.status = 'deleted'
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.deleted_reason = reason
        self.save()


class HotelBooking(TimeStampedModel):
    """Hotel booking details"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='hotel_details')
    room_type = models.ForeignKey(RoomType, on_delete=models.PROTECT)
    
    check_in = models.DateField()
    check_out = models.DateField()
    
    number_of_rooms = models.IntegerField(default=1)
    number_of_adults = models.IntegerField(default=1)
    number_of_children = models.IntegerField(default=0)
    
    total_nights = models.IntegerField()
    
    def __str__(self):
        return f"Hotel Booking - {self.booking.booking_id}"


class BusBooking(TimeStampedModel):
    """Bus booking details"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='bus_details')
    bus_schedule = models.ForeignKey(BusSchedule, on_delete=models.PROTECT)
    bus_route = models.ForeignKey(BusRoute, on_delete=models.PROTECT, null=True, blank=True)
    
    journey_date = models.DateField()
    boarding_point = models.CharField(max_length=200, blank=True)
    dropping_point = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Bus Booking - {self.booking.booking_id}"
    
    @property
    def bus_name(self):
        """Get bus name/number"""
        return self.bus_schedule.route.bus.bus_number if self.bus_schedule else ""
    
    @property
    def total_seats_booked(self):
        """Get total seats booked"""
        return self.seats.count()


class BusBookingSeat(models.Model):
    """Seats booked for bus"""
    bus_booking = models.ForeignKey(BusBooking, on_delete=models.CASCADE, related_name='seats')
    seat = models.ForeignKey(SeatLayout, on_delete=models.PROTECT)
    
    passenger_name = models.CharField(max_length=200)
    passenger_age = models.IntegerField()
    passenger_gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    
    class Meta:
        unique_together = ['bus_booking', 'seat']
    
    def __str__(self):
        return f"{self.bus_booking.booking.booking_id} - Seat {self.seat.seat_number}"


class PackageBooking(TimeStampedModel):
    """Package booking details"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='package_details')
    package_departure = models.ForeignKey(PackageDeparture, on_delete=models.PROTECT)
    
    number_of_travelers = models.IntegerField(default=1)
    
    def __str__(self):
        return f"Package Booking - {self.booking.booking_id}"


class PackageBookingTraveler(models.Model):
    """Travelers for package booking"""
    package_booking = models.ForeignKey(PackageBooking, on_delete=models.CASCADE, related_name='travelers')
    
    name = models.CharField(max_length=200)
    age = models.IntegerField()
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    passport_number = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.package_booking.booking.booking_id} - {self.name}"


class Review(TimeStampedModel):
    """Review for bookings"""
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Review for {self.booking.booking_id} - {self.rating} stars"


class BookingAuditLog(TimeStampedModel):
    """Audit log for booking changes"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='audit_logs')
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    field_name = models.CharField(max_length=100)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    
    action = models.CharField(max_length=50, default='updated', help_text='updated, deleted, restored, etc.')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Log for {self.booking.booking_id} - {self.field_name} by {self.edited_by}"


class InventoryLock(TimeStampedModel):
    """Track inventory locks for both external and internal channel managers."""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('confirmed', 'Confirmed'),
        ('released', 'Released'),
        ('expired', 'Expired'),
        ('failed', 'Failed'),
    ]

    SOURCE_CHOICES = [
        ('external_cm', 'External Channel Manager'),
        ('internal_cm', 'Internal Channel Manager'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventory_lock')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='inventory_locks')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='inventory_locks')

    reference_id = models.CharField(max_length=80, unique=True)
    lock_id = models.CharField(max_length=128, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    provider = models.CharField(max_length=100, blank=True)

    check_in = models.DateField()
    check_out = models.DateField()
    num_rooms = models.IntegerField(default=1)

    expires_at = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Lock {self.reference_id} ({self.get_status_display()})"
