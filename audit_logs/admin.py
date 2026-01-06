from django.contrib import admin
from .models import AuditEntry


@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ('module', 'object_pk', 'action', 'actor', 'created_at', 'channel')
    search_fields = ('module', 'object_pk', 'actor__username', 'field_name', 'notes')
    readonly_fields = ('module', 'object_pk', 'action', 'actor', 'field_name', 'old_value', 'new_value', 'channel', 'notes', 'created_at')
    list_filter = ('module', 'action', 'channel', 'created_at')

    def has_add_permission(self, request):
        return False
