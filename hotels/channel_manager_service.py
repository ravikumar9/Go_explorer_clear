import logging
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

import requests
from django.conf import settings
from django.db import transaction
from django.db.models import Min
from django.utils import timezone

from bookings.models import InventoryLock
from .models import ChannelManagerRoomMapping, Hotel, RoomAvailability, RoomType

logger = logging.getLogger(__name__)


class InventoryLockError(Exception):
    """Raised when inventory cannot be locked."""


class AvailabilityError(Exception):
    """Raised when availability cannot be fetched."""


def _ensure_date(value):
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _date_range(start: date, end: date):
    current = start
    while current < end:
        yield current
        current += timedelta(days=1)


class ExternalChannelManagerClient:
    """Simple HTTP client for external channel manager integrations."""

    def __init__(self, provider: str = "generic", base_url: Optional[str] = None, api_key: Optional[str] = None, timeout: Optional[int] = None):
        self.provider = provider
        self.base_url = base_url or getattr(settings, "CHANNEL_MANAGER_API_BASE_URL", None)
        self.api_key = api_key or getattr(settings, "CHANNEL_MANAGER_API_KEY", None)
        self.timeout = timeout or getattr(settings, "CHANNEL_MANAGER_TIMEOUT", 10)

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _stub_rate(self, mapping: ChannelManagerRoomMapping):
        return {
            "available_rooms": mapping.room_type.total_rooms,
            "rate": float(mapping.room_type.base_price),
            "currency": "INR",
            "restrictions": {},
        }

    def fetch_availability(self, mapping: ChannelManagerRoomMapping, check_in, check_out, num_rooms: int = 1):
        check_in = _ensure_date(check_in)
        check_out = _ensure_date(check_out)

        if not self.base_url or not self.api_key:
            return self._stub_rate(mapping)

        payload = {
            "room_id": mapping.external_room_id,
            "rooms": num_rooms,
            "checkin": check_in.isoformat(),
            "checkout": check_out.isoformat(),
        }
        try:
            response = requests.post(
                f"{self.base_url.rstrip('/')}/availability",
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to fetch availability from CM", exc_info=exc)
            raise AvailabilityError(str(exc)) from exc

    def lock_inventory(self, mapping: ChannelManagerRoomMapping, check_in, check_out, num_rooms: int = 1, hold_minutes: int = 10):
        check_in = _ensure_date(check_in)
        check_out = _ensure_date(check_out)

        if not self.base_url or not self.api_key:
            expires_at = timezone.now() + timedelta(minutes=hold_minutes)
            return {"lock_id": f"SIM-{uuid.uuid4().hex}", "expires_at": expires_at}

        payload = {
            "room_id": mapping.external_room_id,
            "rooms": num_rooms,
            "checkin": check_in.isoformat(),
            "checkout": check_out.isoformat(),
            "reference_id": f"GOEXP-{uuid.uuid4().hex[:10].upper()}",
        }
        try:
            response = requests.post(
                f"{self.base_url.rstrip('/')}/locks",
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            expiry = data.get("lock_expiry_time")
            expires_at = timezone.now() + timedelta(minutes=hold_minutes)
            if expiry:
                try:
                    expires_at = datetime.fromisoformat(expiry)
                    if timezone.is_naive(expires_at):
                        expires_at = timezone.make_aware(expires_at)
                except Exception:  # pragma: no cover
                    expires_at = timezone.now() + timedelta(minutes=hold_minutes)
            return {"lock_id": data.get("lock_id"), "expires_at": expires_at}
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Failed to lock inventory with CM", exc_info=exc)
            raise InventoryLockError(str(exc)) from exc

    def confirm_booking(self, lock_id: str, reference_id: str):
        if not self.base_url or not self.api_key:
            return {"cm_booking_id": f"SIM-BOOK-{uuid.uuid4().hex[:12].upper()}", "status": "confirmed"}

        payload = {"lock_id": lock_id, "reference_id": reference_id}
        try:
            response = requests.post(
                f"{self.base_url.rstrip('/')}/confirm",
                json=payload,
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to confirm booking with CM", exc_info=exc)
            raise InventoryLockError(str(exc)) from exc

    def release_lock(self, lock_id: str):
        if not self.base_url or not self.api_key:
            return {"status": "released"}

        try:
            response = requests.post(
                f"{self.base_url.rstrip('/')}/locks/{lock_id}/release",
                headers=self._headers(),
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to release CM lock", exc_info=exc)
            raise InventoryLockError(str(exc)) from exc


class InternalInventoryService:
    """Inventory and locking for properties managed internally."""

    def __init__(self, hotel: Hotel):
        self.hotel = hotel

    def ensure_availability_rows(self, room_type: RoomType, check_in: date, check_out: date):
        for day in _date_range(check_in, check_out):
            RoomAvailability.objects.get_or_create(
                room_type=room_type,
                date=day,
                defaults={"available_rooms": room_type.total_rooms, "price": room_type.base_price},
            )

    def summarize(self, room_type: RoomType, check_in: date, check_out: date):
        self.ensure_availability_rows(room_type, check_in, check_out)
        qs = RoomAvailability.objects.filter(room_type=room_type, date__gte=check_in, date__lt=check_out)
        available = qs.aggregate(min_rooms=Min("available_rooms")).get("min_rooms")
        rate = qs.aggregate(min_rate=Min("price")).get("min_rate") or room_type.base_price
        return {"available_rooms": available, "rate": float(rate), "currency": "INR"}

    def lock_inventory(self, room_type: RoomType, check_in, check_out, num_rooms: int = 1, hold_minutes: int = 10):
        check_in = _ensure_date(check_in)
        check_out = _ensure_date(check_out)

        with transaction.atomic():
            self.ensure_availability_rows(room_type, check_in, check_out)
            slots = list(
                RoomAvailability.objects.select_for_update()
                .filter(room_type=room_type, date__gte=check_in, date__lt=check_out)
                .order_by("date")
            )

            for slot in slots:
                if slot.available_rooms < num_rooms:
                    raise InventoryLockError(
                        f"Only {slot.available_rooms} rooms left for {slot.date}. Requested {num_rooms}."
                    )

            for slot in slots:
                slot.available_rooms -= num_rooms
                slot.save(update_fields=["available_rooms"])

            reference_id = f"ICM-{uuid.uuid4().hex[:10].upper()}"
            lock = InventoryLock.objects.create(
                hotel=self.hotel,
                room_type=room_type,
                reference_id=reference_id,
                lock_id=reference_id,
                source="internal_cm",
                provider="internal",
                check_in=check_in,
                check_out=check_out,
                num_rooms=num_rooms,
                expires_at=timezone.now() + timedelta(minutes=hold_minutes),
                payload={"type": "hold"},
            )
            return lock

    def confirm_lock(self, lock: InventoryLock):
        if lock.source != "internal_cm":
            return lock
        lock.status = "confirmed"
        lock.save(update_fields=["status", "updated_at"])
        return lock

    def release_lock(self, lock: InventoryLock):
        if lock.source != "internal_cm" or lock.status != "active":
            return lock

        check_in = lock.check_in
        check_out = lock.check_out
        with transaction.atomic():
            slots = list(
                RoomAvailability.objects.select_for_update()
                .filter(room_type=lock.room_type, date__gte=check_in, date__lt=check_out)
                .order_by("date")
            )
            for slot in slots:
                slot.available_rooms += lock.num_rooms
                slot.save(update_fields=["available_rooms"])
            lock.status = "released"
            lock.save(update_fields=["status", "updated_at"])
        return lock


def get_hotel_availability_snapshot(hotel: Hotel, check_in, check_out, num_rooms: int = 1):
    check_in = _ensure_date(check_in)
    check_out = _ensure_date(check_out)

    if hotel.inventory_source == "external_cm":
        mapping = ChannelManagerRoomMapping.objects.filter(hotel=hotel, is_active=True).select_related("room_type").first()
        if not mapping:
            raise AvailabilityError("No active channel manager mapping for this hotel")
        client = ExternalChannelManagerClient(provider=mapping.provider)
        data = client.fetch_availability(mapping, check_in, check_out, num_rooms)
        return {
            "source": "external_cm",
            "available_rooms": data.get("available_rooms"),
            "rate": data.get("rate"),
            "currency": data.get("currency", "INR"),
            "restrictions": data.get("restrictions", {}),
            "provider": mapping.provider,
        }

    # Internal inventory
    room_type = hotel.room_types.first()
    if not room_type:
        raise AvailabilityError("Hotel has no configured room types")

    service = InternalInventoryService(hotel)
    summary = service.summarize(room_type, check_in, check_out)
    summary.update({"source": "internal_cm", "provider": "internal"})
    return summary


def finalize_booking_after_payment(booking, payment_reference: Optional[str] = None):
    """Finalize inventory after successful payment."""
    lock = getattr(booking, "inventory_lock", None)
    if payment_reference:
        booking.payment_reference = payment_reference

    if not lock:
        booking.status = "confirmed"
        booking.save(update_fields=["status", "payment_reference", "updated_at"])
        return booking

    if lock.source == "external_cm":
        client = ExternalChannelManagerClient(provider=lock.provider)
        response = client.confirm_booking(lock.lock_id or lock.reference_id, str(booking.booking_id))
        booking.cm_booking_id = response.get("cm_booking_id", booking.cm_booking_id)
        booking.inventory_channel = "external_cm"
        lock.status = "confirmed"
        lock.save(update_fields=["status", "updated_at"])
    else:
        InternalInventoryService(lock.hotel).confirm_lock(lock)
        booking.inventory_channel = "internal_cm"

    booking.status = "confirmed"
    booking.save(update_fields=["status", "cm_booking_id", "inventory_channel", "payment_reference", "updated_at"])
    return booking


def release_inventory_on_failure(booking):
    lock = getattr(booking, "inventory_lock", None)
    if not lock:
        return

    if lock.source == "external_cm":
        try:
            ExternalChannelManagerClient(provider=lock.provider).release_lock(lock.lock_id or lock.reference_id)
            lock.status = "released"
            lock.save(update_fields=["status", "updated_at"])
        except InventoryLockError:
            pass
    else:
        InternalInventoryService(lock.hotel).release_lock(lock)


def expire_stale_locks():
    """Expire active locks whose hold window has elapsed."""
    now = timezone.now()
    stale_locks = InventoryLock.objects.filter(status="active", expires_at__lte=now)

    for lock in stale_locks:
        if lock.source == "internal_cm":
            InternalInventoryService(lock.hotel).release_lock(lock)
        else:
            lock.status = "expired"
            lock.save(update_fields=["status", "updated_at"])

