from django.db import models
from django.conf import settings
from core.models import TimeStampedModel, City


class PropertyType(models.Model):
    """Types of properties"""
    TYPES = [
        ('homestay', 'Homestay'),
        ('resort', 'Resort'),
        ('villa', 'Villa'),
        ('guesthouse', 'Guest House'),
        ('farmstay', 'Farm Stay'),
        ('houseboat', 'Houseboat'),
    ]
    
    name = models.CharField(max_length=50, choices=TYPES, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.get_name_display()


class PropertyOwner(TimeStampedModel):
    """Property owner profile for homestays, resorts, villas"""
    VERIFICATION_STATUS = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='property_owner_profile')
    
    # Business Details
    business_name = models.CharField(max_length=200)
    property_type = models.ForeignKey(PropertyType, on_delete=models.SET_NULL, null=True)
    description = models.TextField(help_text="Description of your property")
    
    # Owner Details
    owner_name = models.CharField(max_length=200)
    owner_phone = models.CharField(max_length=20)
    owner_email = models.EmailField()
    
    # Property Location
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Legal Details
    gst_number = models.CharField(max_length=20, blank=True, help_text="Optional: GST registration number")
    pan_number = models.CharField(max_length=20, blank=True, help_text="Optional: PAN for tax purposes")
    business_license = models.CharField(max_length=100, blank=True)
    
    # Bank Details
    bank_account_name = models.CharField(max_length=200, blank=True)
    bank_account_number = models.CharField(max_length=20, blank=True)
    bank_ifsc = models.CharField(max_length=20, blank=True)
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_property_owners')
    verification_notes = models.TextField(blank=True)
    
    # Ratings
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.business_name} by {self.owner_name}"


class Property(TimeStampedModel):
    """Individual property listings"""
    owner = models.ForeignKey(PropertyOwner, on_delete=models.CASCADE, related_name='properties')
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    amenities = models.TextField(help_text="Comma-separated list of amenities")
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per night")
    currency = models.CharField(max_length=3, default='INR')
    
    # Capacity
    max_guests = models.IntegerField(default=2)
    num_bedrooms = models.IntegerField(default=1)
    num_bathrooms = models.IntegerField(default=1)
    
    # Media
    image = models.ImageField(upload_to='properties/', null=True, blank=True)
    
    # Rating & Reviews
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-is_featured', '-average_rating', 'name']
    
    def __str__(self):
        return f"{self.name} by {self.owner.business_name}"


class PropertyBooking(TimeStampedModel):
    """Booking for properties"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='bookings')
    guest_name = models.CharField(max_length=200)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    
    check_in = models.DateField()
    check_out = models.DateField()
    num_guests = models.IntegerField(default=1)
    
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    special_requests = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Booking at {self.property.name} by {self.guest_name}"


class PropertyImage(TimeStampedModel):
    """Images for a property listing"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/', null=True, blank=True)
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.property.name}"


class PropertyAmenity(models.Model):
    """Catalog of amenities that properties can reference"""
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True)
    icon = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name
