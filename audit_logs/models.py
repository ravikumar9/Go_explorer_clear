from django.db import models
from django.conf import settings
from core.models import TimeStampedModel


class AuditEntry(TimeStampedModel):
    """Generic audit entry for actions across modules."""
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    module = models.CharField(max_length=100, help_text='e.g., bookings, hotels, partners')
    object_pk = models.CharField(max_length=255)
    action = models.CharField(max_length=50, help_text='created, updated, deleted, synced')
    field_name = models.CharField(max_length=100, blank=True)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    channel = models.CharField(max_length=100, blank=True, help_text='Channel involved (if any)')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.module}:{self.object_pk} {self.action} by {self.actor}"
