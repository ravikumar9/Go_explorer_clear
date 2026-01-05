from ..bus_channel_base import BusChannelBase


class RedbusAdapter(BusChannelBase):
    """Stub adapter for RedBus. Fill network calls and auth handling here.

    Example usage:
        adapter = RedbusAdapter(credentials)
        resp = adapter.create_booking(payload)
"""

    def push_inventory(self, inventory_data: dict) -> dict:
        raise NotImplementedError('Implement Redbus inventory push')

    def fetch_inventory(self, params: dict) -> dict:
        raise NotImplementedError('Implement Redbus inventory fetch')

    def create_booking(self, booking_payload: dict) -> dict:
        raise NotImplementedError('Implement Redbus create booking')

    def cancel_booking(self, external_booking_id: str, reason: str = '') -> dict:
        raise NotImplementedError('Implement Redbus cancel booking')
