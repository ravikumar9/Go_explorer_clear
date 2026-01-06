from django.contrib import admin
from .models import Hotel, HotelImage, RoomType, RoomAvailability, ChannelManagerRoomMapping


class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1


class RoomTypeInline(admin.TabularInline):
    model = RoomType
    extra = 1
    fields = ['name', 'room_type', 'max_occupancy', 'base_price', 'total_rooms', 'is_available']


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'star_rating', 'review_rating', 'is_featured', 'is_active']
    list_filter = ['star_rating', 'is_featured', 'is_active', 'city']
    search_fields = ['name', 'city__name', 'address']
    list_editable = ['is_featured', 'is_active']
    list_select_related = ['city']
    inlines = [HotelImageInline, RoomTypeInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'city', 'address', 'latitude', 'longitude')
        }),
        ('Image', {
            'fields': ('image',),
            'description': 'Hotel main image (will be used as thumbnail)'
        }),
        ('Ratings & Reviews', {
            'fields': ('star_rating', 'review_rating', 'review_count')
        }),
        ('Inventory & Channel Manager', {
            'fields': ('inventory_source', 'channel_manager_name')
        }),
        ('Amenities', {
            'fields': ('has_wifi', 'has_parking', 'has_pool', 'has_gym', 'has_restaurant', 'has_spa', 'has_ac')
        }),
        ('Check-in/Check-out', {
            'fields': ('checkin_time', 'checkout_time')
        }),
        ('Contact', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Status', {
            'fields': ('is_featured', 'is_active')
        }),
    )


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'hotel', 'room_type', 'max_occupancy', 'base_price', 'total_rooms', 'is_available']
    list_filter = ['room_type', 'is_available', 'hotel__city']
    search_fields = ['name', 'hotel__name']
    list_select_related = ['hotel', 'hotel__city']
    list_editable = ['is_available']


@admin.register(RoomAvailability)
class RoomAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['room_type', 'date', 'available_rooms', 'price']
    list_select_related = ['room_type', 'room_type__hotel']
    list_filter = ['date', 'room_type__hotel']
    search_fields = ['room_type__name', 'room_type__hotel__name']
    date_hierarchy = 'date'


@admin.register(ChannelManagerRoomMapping)
class ChannelManagerRoomMappingAdmin(admin.ModelAdmin):
    list_display = ['hotel', 'room_type', 'provider', 'external_room_id', 'is_active']
    list_filter = ['provider', 'is_active', 'hotel__city']
    search_fields = ['hotel__name', 'room_type__name', 'external_room_id']
    list_select_related = ['hotel', 'room_type']
