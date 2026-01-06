from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, date
from core.models import TimeStampedModel, City


class Hotel(TimeStampedModel):
    """Hotel model"""
    STAR_RATINGS = [
        (1, '1 Star'),
        (2, '2 Star'),
        (3, '3 Star'),
        (4, '4 Star'),
        (5, '5 Star'),
    ]

    INVENTORY_SOURCES = [
        ('external_cm', 'External Channel Manager'),
        ('internal_cm', 'Internal (GoExplorer)'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hotels')
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    star_rating = models.IntegerField(choices=STAR_RATINGS, default=3)
    review_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=0
    )
    review_count = models.IntegerField(default=0)
    
    image = models.ImageField(upload_to='hotels/', null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Inventory ownership
    inventory_source = models.CharField(
        max_length=20,
        choices=INVENTORY_SOURCES,
        default='internal_cm',
        help_text="Defines whether this property is managed by an external channel manager or GoExplorer internal inventory",
    )
    channel_manager_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional external channel manager provider name",
    )
    
    # Amenities
    has_wifi = models.BooleanField(default=True)
    has_parking = models.BooleanField(default=False)
    has_pool = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)
    has_restaurant = models.BooleanField(default=False)
    has_spa = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=True)
    
    checkin_time = models.TimeField(default='14:00')
    checkout_time = models.TimeField(default='11:00')
    
    # GST (Goods and Services Tax)
    gst_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=18.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="GST percentage (default: 18%)"
    )
    
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    
    class Meta:
        ordering = ['-is_featured', '-review_rating', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.city.name}"

    # Image helpers
    def get_primary_image(self):
        """Return the primary image file with sensible fallbacks."""
        if self.image:
            return self.image

        primary = self.images.filter(is_primary=True).first()
        if primary:
            return primary.image

        first = self.images.first()
        return first.image if first else None

    @property
    def primary_image_url(self):
        image = self.get_primary_image()
        return image.url if image else ''


class HotelImage(models.Model):
    """Additional images for hotels"""
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hotels/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.hotel.name} - Image"



class RoomType(TimeStampedModel):
    """Room types for hotels"""
    ROOM_TYPES = [
        ('standard', 'Standard Room'),
        ('deluxe', 'Deluxe Room'),
        ('suite', 'Suite'),
        ('family', 'Family Room'),
        ('executive', 'Executive Room'),
    ]
    
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_types')
    name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='standard')
    description = models.TextField()
    
    max_occupancy = models.IntegerField(default=2)
    number_of_beds = models.IntegerField(default=1)
    room_size = models.IntegerField(help_text='Size in square feet', null=True, blank=True)
    
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Room amenities
    has_balcony = models.BooleanField(default=False)
    has_tv = models.BooleanField(default=True)
    has_minibar = models.BooleanField(default=False)
    has_safe = models.BooleanField(default=False)
    
    total_rooms = models.IntegerField(default=1)
    is_available = models.BooleanField(default=True)
    
    image = models.ImageField(upload_to='hotels/rooms/', null=True, blank=True)
    
    class Meta:
        ordering = ['hotel', 'base_price']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.name}"


class ChannelManagerRoomMapping(TimeStampedModel):
    """Maps internal room types to external channel manager room identifiers."""

    PROVIDER_CHOICES = [
        ('generic', 'Generic'),
        ('staah', 'STAAH'),
        ('ratehawk', 'RateHawk'),
        ('djubo', 'Djubo'),
        ('other', 'Other'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='channel_mappings')
    room_type = models.OneToOneField('RoomType', on_delete=models.CASCADE, related_name='channel_mapping')
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, default='generic')
    external_room_id = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['hotel__name', 'room_type__name']
        verbose_name = 'Channel Manager Mapping'
        verbose_name_plural = 'Channel Manager Mappings'

    def __str__(self):
        return f"{self.hotel.name} -> {self.external_room_id} ({self.provider})"


class RoomAvailability(models.Model):
    """Track room availability by date"""
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='availability')
    date = models.DateField()
    available_rooms = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['room_type', 'date']
        ordering = ['date']
    
    def __str__(self):
        return f"{self.room_type} - {self.date}"


class HotelDiscount(TimeStampedModel):
    """Discounts for hotels/rooms"""
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
        ('cashback', 'Cashback'),
    ]
    
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='discounts')
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='percentage')
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    description = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # Validity
    valid_from = models.DateTimeField(default=timezone.now)
    valid_till = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Conditions
    min_booking_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    max_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum discount amount if type is percentage"
    )
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-valid_from']
    
    def __str__(self):
        return f"{self.hotel.name} - {self.description}"
    
    def is_valid(self):
        """Check if discount is still valid"""
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_till and
            (self.usage_limit is None or self.usage_count < self.usage_limit)
        )
    
    def calculate_discount(self, amount):
        """Calculate discount for given amount"""
        if amount < self.min_booking_amount:
            return Decimal('0.00')
        
        if self.discount_type == 'percentage':
            discount = (amount * self.discount_value) / Decimal('100')
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return discount
        elif self.discount_type == 'fixed':
            return min(self.discount_value, amount)
        elif self.discount_type == 'cashback':
            return self.discount_value
        return Decimal('0.00')


class PriceLog(TimeStampedModel):
    """Log for price changes (audit trail)"""
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='price_logs')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    change_date = models.DateField(null=True, blank=True, help_text="Date when price changes take effect")
    reason = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.room_type} - {self.old_price} -> {self.new_price}"
