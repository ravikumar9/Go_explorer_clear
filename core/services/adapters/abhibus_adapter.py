from ..bus_channel_base import BusChannelBase


class AbhiBusAdapter(BusChannelBase):
    """Stub adapter for AbhiBus provider."""

    def push_inventory(self, inventory_data: dict) -> dict:
        raise NotImplementedError()

    def fetch_inventory(self, params: dict) -> dict:
        raise NotImplementedError()

    def create_booking(self, booking_payload: dict) -> dict:
        raise NotImplementedError()

    def cancel_booking(self, external_booking_id: str, reason: str = '') -> dict:
        raise NotImplementedError()
