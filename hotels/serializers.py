from rest_framework import serializers
from datetime import date
from django.db.models import Min
from .models import Hotel, RoomType, HotelImage, RoomAvailability, HotelDiscount, PriceLog
from .pricing_service import PricingCalculator


class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['id', 'image', 'caption', 'is_primary']


class RoomAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomAvailability
        fields = ['id', 'date', 'available_rooms', 'price']


class RoomTypeSerializer(serializers.ModelSerializer):
    availability = RoomAvailabilitySerializer(many=True, read_only=True)
    amenities = serializers.SerializerMethodField()
    
    class Meta:
        model = RoomType
        fields = [
            'id', 'name', 'room_type', 'description', 'max_occupancy',
            'number_of_beds', 'room_size', 'base_price', 'has_balcony',
            'has_tv', 'has_minibar', 'has_safe', 'total_rooms',
            'is_available', 'image', 'availability', 'amenities'
        ]
    
    def get_amenities(self, obj):
        return {
            'balcony': obj.has_balcony,
            'tv': obj.has_tv,
            'minibar': obj.has_minibar,
            'safe': obj.has_safe,
        }


class HotelDiscountSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = HotelDiscount
        fields = [
            'id', 'discount_type', 'discount_value', 'description', 'code',
            'valid_from', 'valid_till', 'min_booking_amount', 'max_discount',
            'usage_limit', 'usage_count', 'is_active', 'is_valid'
        ]
    
    def get_is_valid(self, obj):
        return obj.is_valid()


class HotelListSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    min_price = serializers.SerializerMethodField()
    amenities = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'city', 'city_name', 'address', 'star_rating',
            'review_rating', 'review_count', 'image', 'is_featured',
            'latitude', 'longitude', 'min_price', 'amenities', 'has_wifi',
            'has_parking', 'has_pool', 'has_gym', 'has_restaurant', 'has_spa'
        ]
    
    def get_min_price(self, obj):
        """Get minimum price from room types"""
        min_price = obj.room_types.aggregate(min_price=Min('base_price'))['min_price']
        return float(min_price) if min_price else 0
    
    def get_amenities(self, obj):
        return {
            'wifi': obj.has_wifi,
            'parking': obj.has_parking,
            'pool': obj.has_pool,
            'gym': obj.has_gym,
            'restaurant': obj.has_restaurant,
            'spa': obj.has_spa,
            'ac': obj.has_ac,
        }


class HotelDetailSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    images = HotelImageSerializer(many=True, read_only=True)
    room_types = RoomTypeSerializer(many=True, read_only=True)
    active_discounts = serializers.SerializerMethodField()
    amenities = serializers.SerializerMethodField()
    
    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'description', 'city', 'city_name', 'address',
            'latitude', 'longitude', 'star_rating', 'review_rating',
            'review_count', 'image', 'images', 'has_wifi', 'has_parking',
            'has_pool', 'has_gym', 'has_restaurant', 'has_spa', 'has_ac',
            'checkin_time', 'checkout_time', 'contact_phone', 'contact_email',
            'room_types', 'is_featured', 'active_discounts', 'amenities',
            'gst_percentage'
        ]
    
    def get_active_discounts(self, obj):
        discounts = obj.discounts.filter(is_active=True)
        return HotelDiscountSerializer(discounts, many=True).data
    
    def get_amenities(self, obj):
        return {
            'wifi': obj.has_wifi,
            'parking': obj.has_parking,
            'pool': obj.has_pool,
            'gym': obj.has_gym,
            'restaurant': obj.has_restaurant,
            'spa': obj.has_spa,
            'ac': obj.has_ac,
        }


class PricingRequestSerializer(serializers.Serializer):
    """Serializer for pricing calculation requests"""
    room_type_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    num_rooms = serializers.IntegerField(default=1, min_value=1)
    discount_code = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError("Check-out must be after check-in")
        return data


class AvailabilityCheckSerializer(serializers.Serializer):
    """Serializer for availability check requests"""
    room_type_id = serializers.IntegerField()
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    num_rooms = serializers.IntegerField(default=1, min_value=1)
    
    def validate(self, data):
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError("Check-out must be after check-in")
        return data


class HotelSearchFilterSerializer(serializers.Serializer):
    """Serializer for hotel search filters"""
    city_id = serializers.IntegerField(required=False)
    check_in = serializers.DateField(required=False)
    check_out = serializers.DateField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    star_rating = serializers.IntegerField(required=False, min_value=1, max_value=5)
    has_wifi = serializers.BooleanField(required=False)
    has_parking = serializers.BooleanField(required=False)
    has_pool = serializers.BooleanField(required=False)
    has_gym = serializers.BooleanField(required=False)
    has_restaurant = serializers.BooleanField(required=False)
    has_spa = serializers.BooleanField(required=False)
    sort_by = serializers.ChoiceField(
        choices=['price_asc', 'price_desc', 'rating_asc', 'rating_desc', 'name'],
        required=False
    )
    page = serializers.IntegerField(default=1, min_value=1)
    page_size = serializers.IntegerField(default=10, min_value=1, max_value=100)
