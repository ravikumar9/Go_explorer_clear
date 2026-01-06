from rest_framework import generics, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from datetime import date
from .models import Bus, BusRoute, BusSchedule, BusOperator
from bookings.models import Booking
from .serializers import BusRouteSerializer, BusScheduleSerializer
from hotels.models import City


def bus_list(request):
    """Display all buses with search and filter"""
    buses = Bus.objects.filter(operator__isnull=False).select_related('operator')
    
    # Search by source and destination cities
    source_city = request.GET.get('source')
    destination_city = request.GET.get('destination')
    travel_date = request.GET.get('travel_date')
    
    # Additional filters
    bus_type = request.GET.get('bus_type')
    ac_filter = request.GET.get('ac')  # 'ac' or 'non_ac'
    bus_age_min = request.GET.get('bus_age_min')
    bus_age_max = request.GET.get('bus_age_max')
    departure_time = request.GET.get('departure_time')  # 'early', 'late'
    boarding_point = request.GET.get('boarding_point')
    
    # Filter buses by routes if search parameters provided
    if source_city or destination_city:
        routes = BusRoute.objects.all()
        if source_city:
            try:
                scid = int(source_city)
                routes = routes.filter(source_city_id=scid)
            except (ValueError, TypeError):
                routes = routes.filter(source_city__name__iexact=source_city)
        if destination_city:
            try:
                dcid = int(destination_city)
                routes = routes.filter(destination_city_id=dcid)
            except (ValueError, TypeError):
                routes = routes.filter(destination_city__name__iexact=destination_city)
        bus_ids = routes.values_list('bus_id', flat=True)
        buses = buses.filter(id__in=bus_ids)
    
    # Filter by bus type
    if bus_type:
        buses = buses.filter(bus_type=bus_type)
    
    # Filter by AC/Non-AC
    if ac_filter == 'ac':
        buses = buses.filter(has_ac=True)
    elif ac_filter == 'non_ac':
        buses = buses.filter(has_ac=False)
    
    # Filter by bus age (manufacturing year)
    current_year = date.today().year
    if bus_age_min:
        min_mfg_year = current_year - int(bus_age_min)
        buses = buses.filter(manufacturing_year__gte=min_mfg_year)
    if bus_age_max:
        max_mfg_year = current_year - int(bus_age_max)
        buses = buses.filter(manufacturing_year__lte=max_mfg_year)
    
    # Filter by departure time (filter routes)
    if departure_time:
        routes = BusRoute.objects.filter(bus__in=buses)
        if departure_time == 'early':
            routes = routes.filter(departure_time__lt='12:00:00')
        elif departure_time == 'late':
            routes = routes.filter(departure_time__gte='12:00:00')
        bus_ids = routes.values_list('bus_id', flat=True).distinct()
        buses = buses.filter(id__in=bus_ids)
    
    # Get all cities for search dropdown
    cities = City.objects.all().order_by('name')

    # Map a best-fit route per bus (respecting search params when provided)
    route_map = {}
    for bus in buses:
        route = None
        if source_city and destination_city:
            # Accept either numeric IDs or city names
            try:
                scid = int(source_city)
                dcid = int(destination_city)
                route = bus.routes.filter(source_city_id=scid, destination_city_id=dcid).first()
            except (ValueError, TypeError):
                route = bus.routes.filter(source_city__name__iexact=source_city, destination_city__name__iexact=destination_city).first()
        if not route:
            route = bus.routes.first()
        if route:
            route_map[bus.id] = route
            bus.selected_route = route
    
    context = {
        'buses': buses,
        'cities': cities,
        'selected_source': source_city,
        'selected_destination': destination_city,
        'selected_date': travel_date,
        'selected_bus_type': bus_type,
        'selected_ac': ac_filter,
        'selected_bus_age_min': bus_age_min,
        'selected_bus_age_max': bus_age_max,
        'selected_departure_time': departure_time,
        'selected_boarding_point': boarding_point,
        'bus_types': Bus.BUS_TYPES,
        'route_map': route_map,
    }
    return render(request, 'buses/bus_list.html', context)


def bus_detail(request, bus_id):
    """Display bus details and booking options with seat layout"""
    from .models import SeatLayout
    from bookings.models import BusBookingSeat
    from datetime import datetime
    
    bus = get_object_or_404(Bus, id=bus_id)
    cities = City.objects.all().order_by('name')
    route_id = request.GET.get('route_id')
    travel_date = request.GET.get('travel_date', '')

    selected_route = None
    if route_id:
        selected_route = bus.routes.filter(id=route_id).first()
    if not selected_route:
        selected_route = bus.routes.first()

    boarding_points = selected_route.boarding_points.all() if selected_route else []
    dropping_points = selected_route.dropping_points.all() if selected_route else []
    conv_fee_pct = 2  # percent convenience fee (placeholder)
    gst_pct = 5       # percent GST on base + fee (placeholder)
    
    # Get seat layout for the bus
    seats = bus.seat_layout.all().order_by('deck', 'row', 'column')
    
    # Get booked seats for the selected date
    booked_seat_ids = []
    if travel_date and selected_route:
        # Get all bookings for this bus on this date
        from bookings.models import BusBooking
        try:
            date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date()
            bookings = BusBooking.objects.filter(
                bus_schedule__route=selected_route,
                bus_schedule__date=date_obj
            )
            booked_seat_ids = BusBookingSeat.objects.filter(
                bus_booking__in=bookings
            ).values_list('seat_id', flat=True)
        except (ValueError, BusBooking.DoesNotExist):
            pass
    
    # Mark booked seats
    for seat in seats:
        seat.is_booked = seat.id in booked_seat_ids
        seat.can_book = not seat.is_booked
    
    # Get passenger gender if user is authenticated for ladies seat filtering
    passenger_gender = None
    if request.user.is_authenticated:
        # Get gender from user profile if available
        if hasattr(request.user, 'gender'):
            passenger_gender = request.user.gender
    
    context = {
        'bus': bus,
        'cities': cities,
        'route': selected_route,
        'boarding_points': boarding_points,
        'dropping_points': dropping_points,
        'travel_date_prefill': travel_date,
        'conv_fee_pct': conv_fee_pct,
        'gst_pct': gst_pct,
        'seats': seats,
        'booked_seat_ids': list(booked_seat_ids),
        'passenger_gender': passenger_gender,
        'seat_types': SeatLayout.RESERVED_FOR_CHOICES,
    }
    return render(request, 'buses/bus_detail.html', context)


@login_required
@require_http_methods(["POST"])
def book_bus(request, bus_id):
    """Handle bus booking with ladies seat validation"""
    from .models import SeatLayout
    from bookings.models import BusBooking, BusBookingSeat
    from datetime import datetime
    
    bus = get_object_or_404(Bus, id=bus_id)
    
    try:
        route_id = request.POST.get('route_id')
        travel_date = request.POST.get('travel_date')
        seat_ids = request.POST.getlist('seat_ids')  # List of seat IDs
        passenger_name = request.POST.get('passenger_name')
        passenger_age = request.POST.get('passenger_age')
        passenger_gender = request.POST.get('passenger_gender')
        boarding_point = request.POST.get('boarding_point')
        dropping_point = request.POST.get('dropping_point')
        
        # Validate passenger gender
        if not passenger_gender or passenger_gender not in ['M', 'F', 'O']:
            messages.error(request, 'Please specify passenger gender')
            return redirect('buses:bus_detail', bus_id=bus_id)
        
        if not seat_ids:
            messages.error(request, 'Please select at least one seat')
            return redirect('buses:bus_detail', bus_id=bus_id)
        
        route = get_object_or_404(BusRoute, id=route_id, bus=bus)
        
        # Validate ladies seats for male passengers
        seats = SeatLayout.objects.filter(id__in=seat_ids)
        for seat in seats:
            if not seat.can_be_booked_by(passenger_gender):
                messages.error(request, 
                    f'Seat {seat.seat_number} is reserved for {seat.get_reserved_for_display()}. '
                    f'Male passengers cannot book ladies seats.')
                return redirect('buses:bus_detail', bus_id=bus_id, 
                               route_id=route_id, travel_date=travel_date)
        
        # Create booking
        date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date()
        schedule, created = BusSchedule.objects.get_or_create(
            route=route,
            date=date_obj,
            defaults={'available_seats': bus.total_seats, 'fare': route.base_fare}
        )
        
        total_amount = float(route.base_fare) * len(seat_ids)
        booking = Booking.objects.create(
            user=request.user,
            booking_type='bus',
            total_amount=total_amount,
            customer_name=passenger_name or request.user.get_full_name() or request.user.username,
            customer_email=request.user.email,
            customer_phone=getattr(request.user, 'phone', '') or '',
        )
        
        # Create bus booking details
        bus_booking = BusBooking.objects.create(
            booking=booking,
            bus_schedule=schedule,
            journey_date=date_obj,
        )
        
        # Create seat bookings
        for seat_id in seat_ids:
            seat = SeatLayout.objects.get(id=seat_id)
            BusBookingSeat.objects.create(
                bus_booking=bus_booking,
                seat=seat,
                passenger_name=passenger_name,
                passenger_age=passenger_age or 0,
                passenger_gender=passenger_gender,
            )
        
        # Update schedule availability
        schedule.book_seats(len(seat_ids))
        
        messages.success(request, f'Bus booked successfully! Booking ID: {booking.booking_id}')
        return redirect('bookings:booking_detail', booking_id=booking.booking_id)
    
    except Exception as e:
        messages.error(request, f'Booking failed: {str(e)}')
        return redirect('buses:bus_detail', bus_id=bus_id)


class BusSearchView(generics.ListAPIView):
    """Search buses by source, destination, and date"""
    
    def get_serializer_class(self):
        return BusScheduleSerializer
    
    def get_queryset(self):
        source_city = self.request.query_params.get('source')
        destination_city = self.request.query_params.get('destination')
        date = self.request.query_params.get('date')
        
        # First get matching routes
        routes = BusRoute.objects.filter(is_active=True)
        
        if source_city:
            try:
                scid = int(source_city)
                routes = routes.filter(source_city_id=scid)
            except (ValueError, TypeError):
                routes = routes.filter(source_city__name__iexact=source_city)
        
        if destination_city:
            try:
                dcid = int(destination_city)
                routes = routes.filter(destination_city_id=dcid)
            except (ValueError, TypeError):
                routes = routes.filter(destination_city__name__iexact=destination_city)
        
        # Then get schedules for these routes
        queryset = BusSchedule.objects.filter(route__in=routes, is_active=True).select_related(
            'route__bus__operator', 'route__source_city', 'route__destination_city'
        )
        
        if date:
            queryset = queryset.filter(date=date)
        
        return queryset.order_by('route__departure_time')
    
    def list(self, request, *args, **kwargs):
        """Override list to provide custom response format"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Transform the data for better frontend consumption
        results = []
        for schedule in queryset:
            if schedule.route and schedule.route.bus:
                results.append({
                    'id': schedule.route.bus.id,
                    'route_id': schedule.route.id,
                    'schedule_id': schedule.id,
                    'bus_number': schedule.route.bus.bus_number,
                    'bus_name': schedule.route.bus.bus_name,
                    'bus_type': schedule.route.bus.bus_type,
                    'operator': schedule.route.bus.operator.name if schedule.route.bus.operator else 'Unknown',
                    'source_city': schedule.route.source_city.name,
                    'destination_city': schedule.route.destination_city.name,
                    'departure_time': schedule.route.departure_time.strftime('%H:%M') if schedule.route.departure_time else '--:--',
                    'arrival_time': schedule.route.arrival_time.strftime('%H:%M') if schedule.route.arrival_time else '--:--',
                    'duration_hours': float(schedule.route.duration_hours) if schedule.route.duration_hours else 0,
                    'distance_km': int(schedule.route.distance_km) if schedule.route.distance_km else 0,
                    'base_fare': float(schedule.route.base_fare) if schedule.route.base_fare else 0,
                    'available_seats': schedule.available_seats,
                    'fare': float(schedule.fare) if schedule.fare else 0,
                    'amenities': {
                        'ac': schedule.route.bus.has_ac,
                        'wifi': schedule.route.bus.has_wifi,
                        'charging': schedule.route.bus.has_charging_point,
                        'blanket': schedule.route.bus.has_blanket,
                        'water': schedule.route.bus.has_water_bottle,
                        'tv': schedule.route.bus.has_tv,
                    }
                })
        
        return Response({
            'count': len(results),
            'results': results
        })


class BusRouteListView(generics.ListAPIView):
    """List all bus routes"""
    queryset = BusRoute.objects.filter(is_active=True)
    serializer_class = BusRouteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['source_city', 'destination_city']
    search_fields = ['route_name', 'source_city__name', 'destination_city__name']


class BusRouteDetailView(generics.RetrieveAPIView):
    """Get bus route details"""
    queryset = BusRoute.objects.filter(is_active=True)
    serializer_class = BusRouteSerializer
