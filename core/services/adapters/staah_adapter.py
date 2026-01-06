from ..hotel_channel_base import HotelChannelBase


class StaahAdapter(HotelChannelBase):
    """Stub adapter for STAAH channel manager."""

    def search_availability(self, params: dict) -> dict:
        raise NotImplementedError()

    def create_booking(self, booking_payload: dict) -> dict:
        raise NotImplementedError()

    def cancel_booking(self, external_booking_id: str, reason: str = '') -> dict:
        raise NotImplementedError()
