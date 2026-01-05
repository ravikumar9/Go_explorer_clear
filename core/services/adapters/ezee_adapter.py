from ..hotel_channel_base import HotelChannelBase


class EzeeAdapter(HotelChannelBase):
    """Stub adapter for eZee hotel channel."""

    def search_availability(self, params: dict) -> dict:
        raise NotImplementedError()

    def create_booking(self, booking_payload: dict) -> dict:
        raise NotImplementedError()

    def cancel_booking(self, external_booking_id: str, reason: str = '') -> dict:
        raise NotImplementedError()
