from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.apps import apps
from .models import AuditEntry


@receiver(pre_save)
def capture_changes(sender, instance, **kwargs):
    """Capture changes for models we care about (bookings for now).

    This is lightweight and writes an AuditEntry before save if there are
    attribute differences. Avoid heavy processing here; background tasks
    should handle expensive work.
    """
    # Only monitor specific models to avoid noise
    if sender.__name__ not in ['Booking']:
        return

    try:
        Model = sender
        if not instance.pk:
            # creation will be handled in post_save
            return
        original = Model.objects.get(pk=instance.pk)
    except Exception:
        return

    # Compare field values simply
    for field in [f.name for f in instance._meta.fields]:
        try:
            old = getattr(original, field)
            new = getattr(instance, field)
        except Exception:
            continue
        if old != new:
            AuditEntry.objects.create(
                actor=None,
                module='bookings',
                object_pk=str(getattr(instance, 'booking_id', instance.pk)),
                action='updated',
                field_name=field,
                old_value=str(old)[:2000],
                new_value=str(new)[:2000],
            )


@receiver(post_save)
def capture_create(sender, instance, created, **kwargs):
    if sender.__name__ not in ['Booking']:
        return
    if created:
        AuditEntry.objects.create(
            actor=None,
            module='bookings',
            object_pk=str(getattr(instance, 'booking_id', instance.pk)),
            action='created',
            notes='Created via system',
        )
