from abc import ABC, abstractmethod


class HotelChannelBase(ABC):
    """Abstract base for hotel channel adapters."""

    def __init__(self, credentials: dict):
        self.credentials = credentials

    @abstractmethod
    def search_availability(self, params: dict) -> dict:
        """Search room availability."""

    @abstractmethod
    def create_booking(self, booking_payload: dict) -> dict:
        """Create booking on remote channel and return channel response."""

    @abstractmethod
    def cancel_booking(self, external_booking_id: str, reason: str = '') -> dict:
        """Cancel booking on remote channel."""
