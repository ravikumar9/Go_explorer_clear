from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q, Count
from datetime import date
from django.http import HttpResponse
import csv
from .models import (
    Booking, HotelBooking, BusBooking, BusBookingSeat,
    PackageBooking, PackageBookingTraveler, Review, BookingAuditLog
)


class BusBookingSeatInline(admin.TabularInline):
    model = BusBookingSeat
    extra = 0
    fields = ('seat', 'passenger_name', 'passenger_age', 'passenger_gender')
    readonly_fields = ('seat',)


class HotelBookingInline(admin.StackedInline):
    model = HotelBooking
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class BusBookingInline(admin.StackedInline):
    model = BusBooking
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('bus_schedule', 'bus_route', 'journey_date', 'boarding_point', 'dropping_point')


class PackageBookingTravelerInline(admin.TabularInline):
    model = PackageBookingTraveler
    extra = 0


class PackageBookingInline(admin.StackedInline):
    model = PackageBooking
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


class BookingAuditLogInline(admin.TabularInline):
    model = BookingAuditLog
    extra = 0
    readonly_fields = ('edited_by', 'created_at', 'field_name', 'old_value', 'new_value', 'action', 'notes')
    can_delete = False
    
    def has_add_permission(self, request):
        return False


def get_status_badge(status):
    """Return colored status badge"""
    colors = {
        'pending': '#FFC107',      # Yellow
        'confirmed': '#28A745',    # Green
        'cancelled': '#DC3545',    # Red
        'completed': '#007BFF',    # Blue
        'refunded': '#6C757D',     # Gray
        'deleted': '#721C24',      # Dark Red
    }
    color = colors.get(status, '#6C757D')
    return format_html(
        '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
        color,
        status.upper()
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id_short', 'customer_name', 'customer_phone',
        'booking_type_badge', 'channel_badge', 'status_badge', 'total_amount',
        'created_at_short', 'action_buttons'
    )
    list_filter = ['booking_type', 'status', 'created_at', 'is_deleted']
    search_fields = [
        'booking_id', 'customer_name', 'customer_phone',
        'customer_email', 'user__username'
    ]
    # include channel related fields for quick lookup
    search_fields += ['external_booking_id', 'channel_reference']
    readonly_fields = [
        'booking_id', 'created_at', 'updated_at',
        'deleted_at', 'deleted_by', 'display_audit_log'
    ]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'booking_type', 'status')
        }),
        ('Channel / Inventory', {
            'fields': (
                'booking_source', 'channel_name', 'channel_reference', 'external_booking_id',
                'sync_status', 'last_synced_at', 'inventory_channel', 'lock_id', 'cm_booking_id', 'payment_reference'
            )
        }),
        ('Customer Details', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'special_requests')
        }),
        ('Financial', {
            'fields': ('total_amount', 'paid_amount')
        }),
        ('Cancellation', {
            'fields': ('cancellation_reason', 'cancelled_at', 'refund_amount'),
            'classes': ('collapse',)
        }),
        ('Soft Delete', {
            'fields': ('is_deleted', 'deleted_reason', 'deleted_at', 'deleted_by'),
            'classes': ('collapse',)
        }),
        ('Audit Log', {
            'fields': ('display_audit_log',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [BookingAuditLogInline]
    
    actions = ['soft_delete_action', 'confirm_booking', 'cancel_booking', 'export_as_csv']
    list_per_page = 10

    class Media:
        css = {
            'all': ('admin_custom/admin.css',)
        }
    
    def get_queryset(self, request):
        """Exclude deleted bookings by default and support simple tabs.

        Tabs supported via `?tab=`: 'today', 'confirmed', 'cancelled'.
        """
        qs = super().get_queryset(request)
        qs = qs.filter(is_deleted=False)

        tab = request.GET.get('tab')
        if tab == 'today':
            today = date.today()
            qs = qs.filter(created_at__date=today)
        elif tab == 'confirmed':
            qs = qs.filter(status='confirmed')
        elif tab == 'cancelled':
            qs = qs.filter(status='cancelled')

        return qs

    def changelist_view(self, request, extra_context=None):
        """Provide counts for tabs and status summary in template."""
        from django.db.models import Count

        # Base queryset excluding deleted
        base_qs = Booking.objects.filter(is_deleted=False)

        counts = {
            'all': base_qs.count(),
            'today': base_qs.filter(created_at__date=date.today()).count(),
            'confirmed': base_qs.filter(status='confirmed').count(),
            'cancelled': base_qs.filter(status='cancelled').count(),
            'pending': base_qs.filter(status='pending').count(),
            'refunded': base_qs.filter(status='refunded').count(),
            'deleted': Booking.objects.filter(is_deleted=True).count(),
        }

        extra_context = extra_context or {}
        extra_context['booking_counts'] = counts

        return super().changelist_view(request, extra_context=extra_context)
    
    def booking_id_short(self, obj):
        """Display shortened booking ID"""
        return str(obj.booking_id)[:8].upper()
    booking_id_short.short_description = 'Booking ID'
    
    def customer_name(self, obj):
        """Display customer name"""
        return obj.customer_name
    
    def customer_phone(self, obj):
        """Display masked customer phone to avoid exposing PII in admin list."""
        try:
            return obj.masked_phone()
        except Exception:
            return obj.customer_phone
    
    def booking_type_badge(self, obj):
        """Return colored booking type badge"""
        colors = {'hotel': '#0dcaf0', 'bus': '#0d6efd', 'package': '#198754'}
        color = colors.get(obj.booking_type, '#6C757D')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_booking_type_display()
        )
    booking_type_badge.short_description = 'Type'

    def channel_badge(self, obj):
        if not obj.channel_name:
            return ''
        return format_html('<span style="background:#343a40; color:white; padding:4px 8px; border-radius:3px;">{}</span>', obj.channel_name)
    channel_badge.short_description = 'Channel'
    
    def status_badge(self, obj):
        """Return colored status badge"""
        return get_status_badge(obj.status)
    status_badge.short_description = 'Status'
    
    def created_at_short(self, obj):
        """Display short created date"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_short.short_description = 'Booked'
    
    def action_buttons(self, obj):
        """Display action buttons as a primary View button and a vertical icon group for edit/delete."""
        change_url = reverse('admin:bookings_booking_change', args=[obj.pk])
        delete_url = reverse('admin:bookings_booking_delete', args=[obj.pk])

        parts = []
        parts.append(f'<div class="action-wrap">')
        parts.append(f'<a class="button view-btn" href="{change_url}">View</a>')
        parts.append(f'<div class="icon-group">')
        parts.append(f'<a class="button edit-btn" href="{change_url}" title="Edit"><img src="/static/admin_custom/icons/edit.svg" alt="Edit" /></a>')
        parts.append('</div>')
        parts.append('</div>')
        html = ''.join(parts)
        return format_html(html)
    action_buttons.short_description = 'Actions'
    
    def display_audit_log(self, obj):
        """Display audit log in readonly field"""
        logs = obj.audit_logs.all()
        if not logs:
            return "No audit logs"
        
        html = '<table style="width: 100%; border-collapse: collapse;"><tr style="background: #f0f0f0;"><th style="border: 1px solid #ddd; padding: 8px;">Field</th><th style="border: 1px solid #ddd; padding: 8px;">Old Value</th><th style="border: 1px solid #ddd; padding: 8px;">New Value</th><th style="border: 1px solid #ddd; padding: 8px;">By</th><th style="border: 1px solid #ddd; padding: 8px;">Time</th></tr>'
        
        for log in logs:
            html += f'''<tr>
                <td style="border: 1px solid #ddd; padding: 8px;">{log.field_name}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{log.old_value[:50]}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{log.new_value[:50]}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{log.edited_by.username if log.edited_by else 'System'}</td>
                <td style="border: 1px solid #ddd; padding: 8px;">{log.created_at.strftime('%Y-%m-%d %H:%M')}</td>
            </tr>'''
        
        html += '</table>'
        return format_html(html)
    display_audit_log.short_description = 'Audit Trail'
    
    def soft_delete_action(self, request, queryset):
        """Action to soft delete bookings"""
        for booking in queryset:
            booking.soft_delete(user=request.user, reason='Deleted via admin action')
        self.message_user(request, f"{queryset.count()} booking(s) soft deleted.")
    soft_delete_action.short_description = "Soft delete selected bookings"

    def export_as_csv(self, request, queryset):
        """Export selected bookings as CSV"""
        meta = self.model._meta
        field_names = ['booking_id', 'customer_name', 'customer_email', 'customer_phone', 'booking_type', 'status', 'total_amount', 'paid_amount', 'created_at']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=bookings_export.csv'

        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            row = [
                str(obj.booking_id),
                obj.customer_name,
                obj.customer_email,
                obj.customer_phone,
                obj.booking_type,
                obj.status,
                f"{obj.total_amount}",
                f"{obj.paid_amount}",
                obj.created_at.strftime('%Y-%m-%d %H:%M'),
            ]
            writer.writerow(row)

        return response
    export_as_csv.short_description = "Export selected bookings to CSV"

    
    def confirm_booking(self, request, queryset):
        """Action to confirm bookings"""
        count = queryset.filter(status='pending').update(status='confirmed')
        for booking in queryset.filter(status='confirmed'):
            BookingAuditLog.objects.create(
                booking=booking,
                edited_by=request.user,
                field_name='status',
                old_value='pending',
                new_value='confirmed',
                action='updated'
            )
        self.message_user(request, f"{count} booking(s) confirmed.")
    confirm_booking.short_description = "Confirm selected bookings"
    
    def cancel_booking(self, request, queryset):
        """Action to cancel bookings"""
        count = queryset.exclude(status__in=['completed', 'cancelled']).update(status='cancelled')
        self.message_user(request, f"{count} booking(s) cancelled.")
    cancel_booking.short_description = "Cancel selected bookings"
    
    def get_inline_instances(self, request, obj=None):
        """Show appropriate inline based on booking type"""
        if not obj:
            return []
        
        inlines = []
        if obj.booking_type == 'hotel':
            inlines.append(HotelBookingInline(self.model, self.admin_site))
        elif obj.booking_type == 'bus':
            inlines.append(BusBookingInline(self.model, self.admin_site))
        elif obj.booking_type == 'package':
            inlines.append(PackageBookingInline(self.model, self.admin_site))
        
        return inlines
    
    def save_model(self, request, obj, form, change):
        """Override save to create audit logs for changes"""
        if change:  # Only for updates
            original = Booking.objects.get(pk=obj.pk)
            
            # Check what changed
            if original.status != obj.status:
                BookingAuditLog.objects.create(
                    booking=obj,
                    edited_by=request.user,
                    field_name='status',
                    old_value=original.status,
                    new_value=obj.status,
                    action='updated'
                )
        
        super().save_model(request, obj, form, change)


@admin.register(BusBooking)
class BusBookingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        """Prevent direct add; BusBooking must be created through Booking inline."""
        return False
    
    list_display = ['booking_id_link', 'bus_name', 'journey_date', 'seats_count', 'total_fare', 'status_badge']
    list_filter = ['journey_date', 'booking__status']
    search_fields = ['booking__booking_id', 'booking__customer_name', 'bus_schedule__route__bus__bus_number']
    readonly_fields = ['created_at', 'updated_at', 'booking']
    inlines = [BusBookingSeatInline]
    
    def booking_id_link(self, obj):
        """Link to booking"""
        url = reverse('admin:bookings_booking_change', args=[obj.booking.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.booking.booking_id)[:8].upper())
    booking_id_link.short_description = 'Booking ID'
    
    def bus_name(self, obj):
        """Get bus name"""
        return obj.bus_schedule.route.bus.bus_number if obj.bus_schedule else '-'
    bus_name.short_description = 'Bus'
    
    def seats_count(self, obj):
        """Get count of booked seats"""
        count = obj.seats.count()
        return format_html(
            '<span style="background: #28A745; color: white; padding: 5px 10px; border-radius: 3px;">{} seats</span>',
            count
        )
    seats_count.short_description = 'Seats Booked'
    
    def total_fare(self, obj):
        """Get total fare"""
        return f"₹{obj.booking.total_amount:,.2f}"
    total_fare.short_description = 'Total Fare'
    
    def status_badge(self, obj):
        """Return colored status badge"""
        return get_status_badge(obj.booking.status)
    status_badge.short_description = 'Status'


@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        """Prevent direct add; HotelBooking must be created through Booking inline."""
        return False

    list_display = ['booking_id_link', 'hotel_name', 'check_in', 'check_out', 'room_count', 'status_badge']
    list_filter = ['check_in', 'booking__status']
    search_fields = ['booking__booking_id', 'booking__customer_name']
    readonly_fields = ['created_at', 'updated_at', 'booking']

    def booking_id_link(self, obj):
        url = reverse('admin:bookings_booking_change', args=[obj.booking.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.booking.booking_id)[:8].upper())
    booking_id_link.short_description = 'Booking ID'

    def hotel_name(self, obj):
        return obj.hotel.name if obj.hotel else '-'
    hotel_name.short_description = 'Hotel'

    def room_count(self, obj):
        return obj.number_of_rooms
    room_count.short_description = 'Rooms'

    def status_badge(self, obj):
        return get_status_badge(obj.booking.status)
    status_badge.short_description = 'Status'



@admin.register(PackageBooking)
class PackageBookingAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        """Prevent direct add; PackageBooking must be created through Booking inline."""
        return False

    list_display = ['booking_id', 'package_name', 'number_of_travelers', 'status_badge', 'created_at']
    list_filter = ['package_departure__departure_date', 'booking__status']
    search_fields = ['booking__booking_id', 'booking__customer_name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [PackageBookingTravelerInline]
    
    def booking_id(self, obj):
        """Get booking ID"""
        return str(obj.booking.booking_id)[:8].upper()
    
    def package_name(self, obj):
        """Get package name"""
        return obj.package_departure.package.name
    package_name.short_description = 'Package'
    
    def status_badge(self, obj):
        """Return colored status badge"""
        return get_status_badge(obj.booking.status)
    status_badge.short_description = 'Status'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'rating_display', 'is_approved_display', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['booking__booking_id', 'comment']
    list_editable = ['is_approved']
    readonly_fields = ['booking', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Review', {
            'fields': ('booking', 'rating', 'comment')
        }),
        ('Status', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def booking_id(self, obj):
        """Get booking ID"""
        return str(obj.booking.booking_id)[:8].upper()
    
    def rating_display(self, obj):
        """Display rating with stars"""
        stars = '⭐' * obj.rating
        return format_html(
            '<span style="font-size: 16px;">{} ({}/5)</span>',
            stars, obj.rating
        )
    rating_display.short_description = 'Rating'
    
    def is_approved_display(self, obj):
        """Display approval status"""
        if obj.is_approved:
            return format_html('<span style="color: green;">✓ Approved</span>')
        return format_html('<span style="color: orange;">⏳ Pending</span>')
    is_approved_display.short_description = 'Approval'


@admin.register(BookingAuditLog)
class BookingAuditLogAdmin(admin.ModelAdmin):
    list_display = ['booking_id', 'field_name', 'old_value_short', 'new_value_short', 'edited_by', 'created_at']
    list_filter = ['action', 'field_name', 'created_at']
    search_fields = ['booking__booking_id', 'edited_by__username']
    readonly_fields = ['booking', 'edited_by', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Audit Information', {
            'fields': ('booking', 'edited_by', 'action')
        }),
        ('Change Details', {
            'fields': ('field_name', 'old_value', 'new_value')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual creation"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion"""
        return False
    
    def booking_id(self, obj):
        """Get booking ID"""
        return str(obj.booking.booking_id)[:8].upper()
    booking_id.short_description = 'Booking ID'
    
    def old_value_short(self, obj):
        """Display shortened old value"""
        return obj.old_value[:50] + '...' if len(obj.old_value) > 50 else obj.old_value
    old_value_short.short_description = 'Old Value'
    
    def new_value_short(self, obj):
        """Display shortened new value"""
        return obj.new_value[:50] + '...' if len(obj.new_value) > 50 else obj.new_value
    new_value_short.short_description = 'New Value'
