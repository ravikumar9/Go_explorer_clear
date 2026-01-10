from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from .models import Package, PackageDeparture
from bookings.models import Booking
from .serializers import PackageListSerializer, PackageDetailSerializer


def package_list(request):
    """Display all packages with search and filter"""
    packages = Package.objects.filter(is_active=True)
    
    # Search filters
    search_destination = request.GET.get('destination', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    # Apply filters
    if search_destination:
        packages = packages.filter(
            Q(name__icontains=search_destination) | 
            Q(description__icontains=search_destination)
        )
    
    if min_price:
        try:
            packages = packages.filter(starting_price__gte=float(min_price))
        except ValueError:
            pass
    
    if max_price:
        try:
            packages = packages.filter(starting_price__lte=float(max_price))
        except ValueError:
            pass
    
    context = {
        'packages': packages.order_by('-created_at'),
        'search_destination': search_destination,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'packages/package_list.html', context)


def package_detail(request, package_id):
    """Display package details and booking options"""
    package = get_object_or_404(Package, id=package_id, is_active=True)
    departures = PackageDeparture.objects.filter(
        package=package,
        available_slots__gt=0
    ).order_by('departure_date')
    
    # Sample itinerary for display
    highlights = [
        'Unforgettable travel experience',
        'Expert guided tours',
        '24/7 travel support',
        'Flexible booking and cancellation',
    ]
    
    context = {
        'package': package,
        'departures': departures,
        'highlights': highlights,
    }
    return render(request, 'packages/package_detail.html', context)


@login_required
@require_http_methods(["POST"])
def book_package(request, package_id):
    """Handle package booking"""
    package = get_object_or_404(Package, id=package_id, is_active=True)
    
    try:
        departure_id = request.POST.get('departure_id')
        num_travelers = int(request.POST.get('num_travelers', 1))
        traveler_name = request.POST.get('traveler_name')
        traveler_email = request.POST.get('traveler_email')
        traveler_phone = request.POST.get('traveler_phone')

        with transaction.atomic():
            departure = PackageDeparture.objects.select_for_update().get(id=departure_id, package=package)
            
            # Check availability with a lock to avoid race conditions
            if departure.available_slots < num_travelers:
                messages.error(request, 'Not enough spots available')
                return redirect('packages:package_detail', package_id=package_id)
            
            # Create booking
            total_amount = float(package.starting_price) * num_travelers
            booking = Booking.objects.create(
                user=request.user,
                booking_type='package',
                total_amount=total_amount,
                customer_name=traveler_name or request.user.get_full_name() or request.user.username,
                customer_email=traveler_email or request.user.email,
                customer_phone=traveler_phone or getattr(request.user, 'phone', ''),
            )
            
            # Create package booking details
            from bookings.models import PackageBooking
            PackageBooking.objects.create(
                booking=booking,
                package_departure=departure,
                number_of_travelers=num_travelers,
            )
            
            # Update spot availability atomically
            departure.available_slots -= num_travelers
            departure.save(update_fields=['available_slots'])
        
        # Redirect to confirmation page instead of showing success message
        return redirect(reverse('bookings:booking-confirm', kwargs={'booking_id': booking.booking_id}))
    
    except Exception as e:
        messages.error(request, f'Booking failed: {str(e)}')
        return redirect('packages:package_detail', package_id=package_id)


class PackageListView(generics.ListAPIView):
    """List all packages with filters"""
    queryset = Package.objects.filter(is_active=True)
    serializer_class = PackageListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['package_type', 'is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['rating', 'starting_price', 'duration_days']


class PackageDetailView(generics.RetrieveAPIView):
    """Get package details"""
    queryset = Package.objects.filter(is_active=True)
    serializer_class = PackageDetailSerializer


class PackageSearchView(generics.ListAPIView):
    """Search packages"""
    serializer_class = PackageListSerializer
    
    def get_queryset(self):
        queryset = Package.objects.filter(is_active=True)
        
        package_type = self.request.query_params.get('type')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        duration = self.request.query_params.get('duration')
        
        if package_type:
            queryset = queryset.filter(package_type=package_type)
        
        if min_price:
            queryset = queryset.filter(starting_price__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(starting_price__lte=max_price)
        
        if duration:
            queryset = queryset.filter(duration_days=duration)
        
        return queryset
