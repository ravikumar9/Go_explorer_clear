from rest_framework import serializers
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = [
            'booking_id', 'booking_type', 'status', 'total_amount', 'paid_amount',
            'customer_name', 'customer_email', 'customer_phone', 'external_booking_id',
            'channel_name', 'channel_reference', 'sync_status', 'last_synced_at',
            'booking_source', 'created_at'
        ]
        read_only_fields = ['booking_id', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Mask PII by default in API responses
        try:
            data['customer_phone'] = instance.masked_phone()
            data['customer_email'] = instance.masked_email()
        except Exception:
            pass
        return data
