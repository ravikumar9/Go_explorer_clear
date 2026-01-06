Channel Adapter Guide
=====================

Overview
--------
This project uses an adapter pattern to integrate with external channel managers
and providers (bus/hotel/package). Adapter interfaces live under
`core/services/*_channel_base.py` and provider-specific adapters live under
`core/services/adapters/`.

How to add a new channel (summary)
---------------------------------
1. Create an adapter module in `core/services/adapters/`, e.g. `mychannel_adapter.py`.
2. Subclass the appropriate base class (`BusChannelBase` or `HotelChannelBase`).
3. Implement the abstract methods: inventory sync, create_booking, cancel_booking, etc.
4. Store credentials securely in environment variables and add them to partner credentials storage.
5. Add a partner record (see `partners` model design) and point to your adapter by name.
6. Wire background tasks (Celery) to call adapter methods for sync/confirmation/cancelation.

Important notes
---------------
- Do not perform blocking HTTP calls on import; adapters should be instantiable with
  credentials and only perform network I/O when methods are called.
- Validate and sanitize all incoming/outgoing data.
- Use `audit_logs` to record channel interactions.
