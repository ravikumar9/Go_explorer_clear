"""Service interfaces and adapters for external channel integrations.

Place adapters under `core.services.adapters` and implement provider-specific
logic there. Core booking/business logic should depend only on the base
interfaces here.
"""

__all__ = [
    'bus_channel_base',
    'hotel_channel_base',
]
