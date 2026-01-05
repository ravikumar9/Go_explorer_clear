from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import date, timedelta
from bookings.models import Booking, BusBooking
from buses.models import BusSchedule, Bus
from hotels.models import Hotel
from packages.models import Package


def is_admin(user):
    """Check if user is admin or staff"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard with booking statistics"""
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    # Booking counts
    total_bookings = Booking.objects.filter(is_deleted=False).count()
    today_bookings = Booking.objects.filter(
        is_deleted=False,
        created_at__date=today
    ).count()
    pending_bookings = Booking.objects.filter(
        is_deleted=False,
        status='pending'
    ).count()
    confirmed_bookings = Booking.objects.filter(
        is_deleted=False,
        status='confirmed'
    ).count()
    cancelled_bookings = Booking.objects.filter(
        is_deleted=False,
        status='cancelled'
    ).count()
    
    # Financial data
    total_revenue = Booking.objects.filter(
        is_deleted=False,
        status='confirmed'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    today_revenue = Booking.objects.filter(
        is_deleted=False,
        status='confirmed',
        created_at__date=today
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    week_revenue = Booking.objects.filter(
        is_deleted=False,
        status='confirmed',
        created_at__date__gte=week_ago
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Bus data
    bus_bookings = BusBooking.objects.filter(
        booking__is_deleted=False
    ).count()
    
    bus_schedules = BusSchedule.objects.filter(
        is_active=True,
        is_cancelled=False
    ).count()
    
    # Get bus occupancy details
    bus_occupancy_data = []
    total_seats = 0
    booked_seats = 0
    
    for schedule in BusSchedule.objects.filter(is_active=True, is_cancelled=False)[:10]:
        total = schedule.available_seats + schedule.booked_seats
        occupancy = (schedule.booked_seats / total * 100) if total > 0 else 0
        
        bus_occupancy_data.append({
            'route': str(schedule.route),
            'date': schedule.date,
            'booked': schedule.booked_seats,
            'available': schedule.available_seats,
            'occupancy_pct': round(occupancy, 1),
        })
        
        total_seats += total
        booked_seats += schedule.booked_seats
    
    overall_occupancy = (booked_seats / total_seats * 100) if total_seats > 0 else 0
    
    # Booking type breakdown
    booking_types = Booking.objects.filter(
        is_deleted=False
    ).values('booking_type').annotate(count=Count('id'))
    
    # Recent bookings
    recent_bookings = Booking.objects.filter(
        is_deleted=False
    ).select_related('user')[:10]
    
    # Pending actions
    pending_approvals = Booking.objects.filter(
        is_deleted=False,
        status='pending'
    ).count()
    
    context = {
        'total_bookings': total_bookings,
        'today_bookings': today_bookings,
        'pending_bookings': pending_bookings,
        'confirmed_bookings': confirmed_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'week_revenue': week_revenue,
        'bus_bookings': bus_bookings,
        'bus_schedules': bus_schedules,
        'overall_occupancy': round(overall_occupancy, 1),
        'bus_occupancy_data': bus_occupancy_data,
        'booking_types': booking_types,
        'recent_bookings': recent_bookings,
        'pending_approvals': pending_approvals,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
