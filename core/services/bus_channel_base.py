from abc import ABC, abstractmethod


class BusChannelBase(ABC):
    """Abstract base for bus channel adapters.

    Implementations must not perform blocking network calls on import.
    All network operations should be exposed as instance methods to be
    called by background tasks.
    """

    def __init__(self, credentials: dict):
        self.credentials = credentials

    @abstractmethod
    def push_inventory(self, inventory_data: dict) -> dict:
        """Push inventory updates to channel. Return response dict."""

    @abstractmethod
    def fetch_inventory(self, params: dict) -> dict:
        """Fetch inventory (availability, seat map, fares)."""

    @abstractmethod
    def create_booking(self, booking_payload: dict) -> dict:
        """Create booking on remote channel and return channel response."""

    @abstractmethod
    def cancel_booking(self, external_booking_id: str, reason: str = '') -> dict:
        """Cancel booking on remote channel."""
