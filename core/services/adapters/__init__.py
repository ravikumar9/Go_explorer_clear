"""Adapters package for external channel providers.

Add new modules here for each provider (redbus, abhibus, ezee, staah, etc.).
Adapters should subclass the corresponding Base classes in core.services.
"""

__all__ = [
    'redbus_adapter',
    'abhibus_adapter',
    'ezee_adapter',
    'staah_adapter',
]
