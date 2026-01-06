from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


class DashboardAdminSite(admin.AdminSite):
    """Custom admin site with dashboard"""
    site_header = "GoExplorer Admin Panel"
    site_title = "GoExplorer"
    
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def index(self, request, extra_context=None):
        """Override admin index to show dashboard"""
        from bookings.models import Booking
        from buses.models import BusSchedule
        from datetime import date, timedelta
        from django.db.models import Count, Sum
        
        today = date.today()
        week_ago = today - timedelta(days=7)
        
        # Key metrics
        extra_context = extra_context or {}
        extra_context.update({
            'total_bookings': Booking.objects.filter(is_deleted=False).count(),
            'today_bookings': Booking.objects.filter(is_deleted=False, created_at__date=today).count(),
            'pending_bookings': Booking.objects.filter(is_deleted=False, status='pending').count(),
            'confirmed_bookings': Booking.objects.filter(is_deleted=False, status='confirmed').count(),
            'cancelled_bookings': Booking.objects.filter(is_deleted=False, status='cancelled').count(),
            'total_revenue': Booking.objects.filter(is_deleted=False, status='confirmed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'today_revenue': Booking.objects.filter(is_deleted=False, status='confirmed', created_at__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
            'week_revenue': Booking.objects.filter(is_deleted=False, status='confirmed', created_at__date__gte=week_ago).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        })
        
        return super().index(request, extra_context)
