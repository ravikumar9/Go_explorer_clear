from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from datetime import datetime
from .models import PropertyType, PropertyOwner, Property, PropertyImage, PropertyAmenity


def get_verification_badge(status):
    """Generate colored badge for verification status"""
    colors = {
        'pending': '#FFC107',      # Yellow
        'verified': '#28A745',     # Green
        'rejected': '#DC3545',     # Red
        'suspended': '#721C24',    # Dark Red
    }
    text_map = {
        'pending': 'PENDING VERIFICATION',
        'verified': 'VERIFIED',
        'rejected': 'REJECTED',
        'suspended': 'SUSPENDED',
    }
    return format_html(
        '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
        colors.get(status, '#6C757D'),
        text_map.get(status, status.upper())
    )


def approve_property_owners(modeladmin, request, queryset):
    """Bulk action to approve pending property owners"""
    updated = 0
    for owner in queryset.filter(verification_status='pending'):
        owner.verification_status = 'verified'
        owner.verified_at = timezone.now()
        owner.verified_by = request.user
        owner.verification_notes = f'Approved by {request.user.get_full_name() or request.user.username} on {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        owner.save()
        updated += 1
    modeladmin.message_user(request, f'✅ {updated} property owner(s) approved successfully!')

approve_property_owners.short_description = '✅ Approve Selected Property Owners'


def reject_property_owners(modeladmin, request, queryset):
    """Bulk action to reject property owners"""
    updated = 0
    for owner in queryset.filter(verification_status='pending'):
        owner.verification_status = 'rejected'
        owner.verified_at = timezone.now()
        owner.verified_by = request.user
        owner.verification_notes = f'Rejected by {request.user.get_full_name() or request.user.username} on {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        owner.save()
        updated += 1
    modeladmin.message_user(request, f'❌ {updated} property owner(s) rejected!')

reject_property_owners.short_description = '❌ Reject Selected Property Owners'


def suspend_property_owners(modeladmin, request, queryset):
    """Bulk action to suspend property owners"""
    updated = 0
    for owner in queryset.exclude(verification_status='pending'):
        owner.verification_status = 'suspended'
        owner.is_active = False
        owner.verified_by = request.user
        owner.verification_notes = f'Suspended by {request.user.get_full_name() or request.user.username} on {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        owner.save()
        updated += 1
    modeladmin.message_user(request, f'⛔ {updated} property owner(s) suspended!')

suspend_property_owners.short_description = '⛔ Suspend Selected Property Owners'


@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    readonly_fields = ('name',)
    
    def has_delete_permission(self, request):
        return False


@admin.register(PropertyOwner)
class PropertyOwnerAdmin(admin.ModelAdmin):
    list_display = (
        'owner_id_short',
        'business_name_short',
        'owner_name',
        'status_badge',
        'verification_date',
        'verified_by_name',
        'rating_display',
        'is_active_display',
        'action_buttons'
    )
    
    list_filter = (
        'verification_status',
        'is_active',
        'created_at',
        'average_rating',
    )
    
    search_fields = (
        'business_name',
        'owner_name',
        'owner_email',
        'owner_phone',
        'gst_number',
        'user__email'
    )
    
    readonly_fields = (
        'user',
        'created_at',
        'updated_at',
        'verified_at',
        'verified_by',
        'average_rating',
        'total_reviews',
        'verification_section',
        'location_map'
    )
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',)
        }),
        ('Business Information', {
            'fields': (
                'business_name',
                'property_type',
                'description',
            )
        }),
        ('Owner Details', {
            'fields': (
                'owner_name',
                'owner_phone',
                'owner_email',
            )
        }),
        ('Property Location', {
            'fields': (
                'city',
                'address',
                'pincode',
                'latitude',
                'longitude',
                'location_map'
            ),
            'classes': ('collapse',)
        }),
        ('Legal & Tax Information', {
            'fields': (
                'gst_number',
                'pan_number',
                'business_license',
            ),
            'classes': ('collapse',)
        }),
        ('Bank Details', {
            'fields': (
                'bank_account_name',
                'bank_account_number',
                'bank_ifsc',
            ),
            'classes': ('collapse',)
        }),
        ('Verification & Approval', {
            'fields': (
                'verification_section',
                'verification_status',
                'verified_at',
                'verified_by',
                'verification_notes',
            ),
            'classes': ('wide',)
        }),
        ('Performance Metrics', {
            'fields': (
                'average_rating',
                'total_reviews',
            ),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        approve_property_owners,
        reject_property_owners,
        suspend_property_owners,
    ]
    
    def get_queryset(self, request):
        """Show all owners, regardless of status"""
        return super().get_queryset(request).select_related('user', 'verified_by', 'property_type', 'city')
    
    def owner_id_short(self, obj):
        """Display shortened owner ID"""
        return format_html(
            '<strong>#{}</strong>',
            str(obj.id)[:8]
        )
    owner_id_short.short_description = 'ID'
    owner_id_short.admin_order_field = 'id'
    
    def business_name_short(self, obj):
        """Display business name, truncated if too long"""
        name = obj.business_name[:30]
        if len(obj.business_name) > 30:
            return f"{name}..."
        return name
    business_name_short.short_description = 'Business'
    business_name_short.admin_order_field = 'business_name'
    
    def status_badge(self, obj):
        """Display colored status badge"""
        return get_verification_badge(obj.verification_status)
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'verification_status'
    
    def verification_date(self, obj):
        """Display verification date"""
        if obj.verified_at:
            return obj.verified_at.strftime('%d-%m-%Y %H:%M')
        return format_html('<span style="color: #999;">-</span>')
    verification_date.short_description = 'Verified Date'
    verification_date.admin_order_field = 'verified_at'
    
    def verified_by_name(self, obj):
        """Display verifier name"""
        if obj.verified_by:
            return obj.verified_by.get_full_name() or obj.verified_by.username
        return format_html('<span style="color: #999;">-</span>')
    verified_by_name.short_description = 'Verified By'
    verified_by_name.admin_order_field = 'verified_by'
    
    def rating_display(self, obj):
        """Display rating with stars"""
        rating = float(obj.average_rating)
        if rating == 0:
            return format_html('<span style="color: #999;">No reviews</span>')
        stars = '⭐' * int(rating)
        partial = '✓' if rating % 1 >= 0.5 else ''
        return format_html(
            '{} {} ({}/5)',
            stars,
            partial,
            obj.average_rating
        )
    rating_display.short_description = 'Rating'
    rating_display.admin_order_field = 'average_rating'
    
    def is_active_display(self, obj):
        """Display active status"""
        if obj.is_active:
            return format_html(
                '<span style="color: #28A745; font-weight: bold;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: #DC3545; font-weight: bold;">✗ Inactive</span>'
        )
    is_active_display.short_description = 'Active'
    is_active_display.admin_order_field = 'is_active'
    
    def action_buttons(self, obj):
        """Display action buttons"""
        buttons = []
        
        # Approve button for pending
        if obj.verification_status == 'pending':
            buttons.append(
                f'<a class="button" style="background-color: #28A745; color: white; padding: 5px 10px; margin-right: 5px; border-radius: 3px;" '
                f'href="#" onclick="approveOwner({obj.id})">✅ Approve</a>'
            )
        
        # Reject button for pending
        if obj.verification_status == 'pending':
            buttons.append(
                f'<a class="button" style="background-color: #DC3545; color: white; padding: 5px 10px; margin-right: 5px; border-radius: 3px;" '
                f'href="#" onclick="rejectOwner({obj.id})">❌ Reject</a>'
            )
        
        # Suspend button for verified
        if obj.verification_status == 'verified' and obj.is_active:
            buttons.append(
                f'<a class="button" style="background-color: #721C24; color: white; padding: 5px 10px; margin-right: 5px; border-radius: 3px;" '
                f'href="#" onclick="suspendOwner({obj.id})">⛔ Suspend</a>'
            )
        
        # Edit button
        change_url = reverse('admin:property_owners_propertyowner_change', args=[obj.id])
        buttons.append(
            f'<a class="button" style="background-color: #007BFF; color: white; padding: 5px 10px; margin-right: 5px; border-radius: 3px;" '
            f'href="{change_url}">📝 Edit</a>'
        )
        
        return format_html('&nbsp;'.join(buttons))
    action_buttons.short_description = 'Actions'
    
    def verification_section(self, obj):
        """Display verification section"""
        status_html = get_verification_badge(obj.verification_status)
        
        html = f'''
        <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px; border-left: 4px solid #007BFF;">
            <div style="margin-bottom: 10px;"><strong>Status:</strong> {status_html}</div>
        '''
        
        if obj.verified_at:
            html += f'<div style="margin-bottom: 10px;"><strong>Verified At:</strong> {obj.verified_at.strftime("%d-%m-%Y %H:%M:%S")}</div>'
        
        if obj.verified_by:
            verified_by = obj.verified_by.get_full_name() or obj.verified_by.username
            html += f'<div style="margin-bottom: 10px;"><strong>Verified By:</strong> {verified_by}</div>'
        
        if obj.verification_notes:
            html += f'<div><strong>Notes:</strong><br/>{obj.verification_notes}</div>'
        
        html += '</div>'
        return format_html(html)
    verification_section.short_description = 'Verification Details'
    
    def location_map(self, obj):
        """Display location on map"""
        if obj.latitude and obj.longitude:
            url = f"https://www.google.com/maps/search/{obj.latitude},{obj.longitude}"
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #007BFF; color: white; padding: 8px 15px; border-radius: 3px; text-decoration: none;">📍 View on Map</a>',
                url
            )
        return format_html('<span style="color: #999;">Location not available</span>')
    location_map.short_description = 'Location'
    
    def save_model(self, request, obj, form, change):
        """Save audit info when model changes"""
        if not change:  # New object
            pass
        super().save_model(request, obj, form, change)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        'property_id_short',
        'name_short',
        'owner_name',
        'owner_city',
        'base_price_display',
        'max_guests_display',
        'created_date',
    )
    
    list_filter = (
        'created_at',
        'owner__city',
        'base_price',
        'max_guests',
    )
    
    search_fields = (
        'name',
        'description',
        'owner__business_name',
        'owner__owner_name',
    )
    
    readonly_fields = (
        'owner',
        'created_at',
        'updated_at',
        'amenities_display',
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'owner',
                'name',
                'description',
            )
        }),
        ('Amenities', {
            'fields': ('amenities_display',)
        }),
        ('Pricing & Capacity', {
            'fields': (
                'base_price',
                'currency',
                'max_guests',
                'num_bedrooms',
                'num_bathrooms',
            )
        }),
        ('Media', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'owner__city')
    
    def property_id_short(self, obj):
        """Display shortened property ID"""
        return format_html('<strong>#{}</strong>', str(obj.id)[:8])
    property_id_short.short_description = 'ID'
    property_id_short.admin_order_field = 'id'
    
    def name_short(self, obj):
        """Display property name, truncated if needed"""
        name = obj.name[:40]
        if len(obj.name) > 40:
            return f"{name}..."
        return name
    name_short.short_description = 'Property Name'
    name_short.admin_order_field = 'name'
    
    def owner_name(self, obj):
        """Display owner business name"""
        return obj.owner.business_name
    owner_name.short_description = 'Owner'
    owner_name.admin_order_field = 'owner__business_name'
    
    def base_price_display(self, obj):
        """Display price with currency"""
        return format_html(
            '₹{:,.2f}',
            obj.base_price
        )
    base_price_display.short_description = 'Price/Night'
    base_price_display.admin_order_field = 'base_price'
    
    def max_guests_display(self, obj):
        """Display guest capacity"""
        return format_html(
            '<span style="background-color: #0dcaf0; color: white; padding: 3px 8px; border-radius: 3px;">{} guests</span>',
            obj.max_guests
        )
    max_guests_display.short_description = 'Capacity'
    max_guests_display.admin_order_field = 'max_guests'
    
    def created_date(self, obj):
        """Display created date"""
        return obj.created_at.strftime('%d-%m-%Y')
    created_date.short_description = 'Created'
    created_date.admin_order_field = 'created_at'
    
    def amenities_display(self, obj):
        """Display amenities as formatted list"""
        if not obj.amenities:
            return format_html('<span style="color: #999;">No amenities listed</span>')
        
        amenities = [a.strip() for a in obj.amenities.split(',')]
        html = '<ul style="list-style-type: none; padding-left: 0;">'
        for amenity in amenities:
            html += f'<li style="padding: 5px; margin-bottom: 5px; background-color: #f0f0f0; border-radius: 3px;">✓ {amenity}</li>'
        html += '</ul>'
        return format_html(html)
    amenities_display.short_description = 'Amenities'

    def owner_city(self, obj):
        if obj.owner and obj.owner.city:
            return obj.owner.city.name
        return format_html('<span style="color: #999;">-</span>')
    owner_city.short_description = 'City'
    owner_city.admin_order_field = 'owner__city'


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = (
        'property_name',
        'image_preview',
        'is_primary_display',
        'created_date',
    )
    
    list_filter = (
        'is_primary',
        'created_at',
    )
    
    search_fields = (
        'property__name',
    )
    
    readonly_fields = (
        'property',
        'created_at',
        'updated_at',
        'image_preview_large',
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property')
    
    def property_name(self, obj):
        """Display property name"""
        return obj.property.name
    property_name.short_description = 'Property'
    property_name.admin_order_field = 'property__name'
    
    def image_preview(self, obj):
        """Show small image preview"""
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="border-radius: 3px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        """Show large image preview"""
        if obj.image:
            return format_html(
                '<img src="{}" width="300" style="border-radius: 5px;" />',
                obj.image.url
            )
        return format_html('<span style="color: #999;">No image</span>')
    image_preview_large.short_description = 'Image Preview'
    
    def is_primary_display(self, obj):
        """Display primary status"""
        if obj.is_primary:
            return format_html('<span style="color: #28A745; font-weight: bold;">⭐ Primary</span>')
        return format_html('<span style="color: #999;">Secondary</span>')
    is_primary_display.short_description = 'Primary'
    is_primary_display.admin_order_field = 'is_primary'
    
    def created_date(self, obj):
        """Display created date"""
        return obj.created_at.strftime('%d-%m-%Y')
    created_date.short_description = 'Created'
    created_date.admin_order_field = 'created_at'


@admin.register(PropertyAmenity)
class PropertyAmenityAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'icon_display',
    )
    
    list_filter = (
        'category',
    )
    
    search_fields = (
        'name',
    )
    
    def icon_display(self, obj):
        """Display amenity icon"""
        if obj.icon:
            return obj.icon
        return format_html('<span style="color: #999;">-</span>')
    icon_display.short_description = 'Icon'
