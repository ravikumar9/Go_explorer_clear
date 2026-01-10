from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Min, Value, FloatField, Q, DecimalField, F
from django.db.models.functions import Coalesce
from datetime import date, datetime, timedelta
from django.views.decorators.http import require_http_methods
from django_filters.rest_framework import DjangoFilterBackend
from decimal import Decimal
from django.utils import timezone
import uuid

from .channel_manager_service import (
    ExternalChannelManagerClient,
    InternalInventoryService,
    InventoryLockError,
    AvailabilityError,
    get_hotel_availability_snapshot,
)
from .models import Hotel, RoomType, RoomAvailability, HotelDiscount, ChannelManagerRoomMapping
from .serializers import (
    HotelListSerializer, HotelDetailSerializer, RoomTypeSerializer,
    PricingRequestSerializer, AvailabilityCheckSerializer,
    HotelSearchFilterSerializer
)
from .pricing_service import PricingCalculator, OccupancyCalculator
from core.models import City
from bookings.models import Booking, HotelBooking, InventoryLock


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================
# HOTEL LISTING & SEARCH APIs
# ============================================

class HotelListView(generics.ListAPIView):
    """List all hotels with filters"""
    queryset = Hotel.objects.filter(is_active=True).prefetch_related('room_types', 'images')
    serializer_class = HotelListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'star_rating', 'is_featured']
    search_fields = ['name', 'description', 'city__name']
    ordering_fields = ['review_rating', 'name']
    pagination_class = StandardResultsSetPagination


class HotelDetailView(generics.RetrieveAPIView):
    """Get hotel details with all room types and amenities"""
    queryset = Hotel.objects.filter(is_active=True).prefetch_related('room_types', 'images', 'discounts')
    serializer_class = HotelDetailSerializer


class HotelSearchView(generics.ListAPIView):
    """
    Advanced hotel search with filters
    
    Query Parameters:
    - city_id: Filter by city
    - check_in: Check-in date (YYYY-MM-DD)
    - check_out: Check-out date (YYYY-MM-DD)
    - min_price: Minimum base price
    - max_price: Maximum base price
    - star_rating: Hotel star rating (1-5)
    - has_wifi, has_parking, has_pool, has_gym, has_restaurant, has_spa: Boolean filters
    - sort_by: price_asc, price_desc, rating_asc, rating_desc, name
    - page: Page number (default 1)
    - page_size: Items per page (default 10)
    """
    serializer_class = HotelListSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        queryset = Hotel.objects.filter(is_active=True).prefetch_related('room_types', 'images')
        
        # City filter
        city_id = self.request.query_params.get('city_id')
        if city_id:
            # Accept either numeric id or city name for backward compatibility
            try:
                cid = int(city_id)
                queryset = queryset.filter(city_id=cid)
            except (ValueError, TypeError):
                queryset = queryset.filter(city__name__iexact=city_id)
        
        # Star rating filter
        star_rating = self.request.query_params.get('star_rating')
        if star_rating:
            queryset = queryset.filter(star_rating=int(star_rating))
        
        # Amenity filters
        if self.request.query_params.get('has_wifi') == 'true':
            queryset = queryset.filter(has_wifi=True)
        if self.request.query_params.get('has_parking') == 'true':
            queryset = queryset.filter(has_parking=True)
        if self.request.query_params.get('has_pool') == 'true':
            queryset = queryset.filter(has_pool=True)
        if self.request.query_params.get('has_gym') == 'true':
            queryset = queryset.filter(has_gym=True)
        if self.request.query_params.get('has_restaurant') == 'true':
            queryset = queryset.filter(has_restaurant=True)
        if self.request.query_params.get('has_spa') == 'true':
            queryset = queryset.filter(has_spa=True)
        
        # Price filter (min price of room types)
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price or max_price:
            queryset = queryset.annotate(
                min_room_price=Coalesce(Min('room_types__base_price'), Value(0, output_field=DecimalField()))
            )
            if min_price:
                queryset = queryset.filter(min_room_price__gte=Decimal(min_price))
            if max_price:
                queryset = queryset.filter(min_room_price__lte=Decimal(max_price))
        
        # Sorting
        sort_by = self.request.query_params.get('sort_by', 'name')
        if sort_by == 'price_asc':
            queryset = queryset.annotate(
                min_room_price=Coalesce(Min('room_types__base_price'), Value(0, output_field=DecimalField()))
            ).order_by('min_room_price')
        elif sort_by == 'price_desc':
            queryset = queryset.annotate(
                max_room_price=Coalesce(F('room_types__base_price'), Value(0, output_field=DecimalField()), output_field=DecimalField())
            ).order_by('-max_room_price')
        elif sort_by == 'rating_asc':
            queryset = queryset.order_by('review_rating')
        elif sort_by == 'rating_desc':
            queryset = queryset.order_by('-review_rating')
        else:
            queryset = queryset.order_by('name')
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['check_in'] = self.request.query_params.get('check_in')
        context['check_out'] = self.request.query_params.get('check_out')
        return context


# ============================================
# PRICING & AVAILABILITY APIs
# ============================================

@api_view(['POST'])
def calculate_price(request):
    """
    Calculate total price for a room booking
    
    Request body:
    {
        "room_type_id": 1,
        "check_in": "2024-01-10",
        "check_out": "2024-01-15",
        "num_rooms": 2,
        "discount_code": "SAVE20" (optional)
    }
    """
    serializer = PricingRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        room_type = RoomType.objects.get(id=serializer.validated_data['room_type_id'])
        calculator = PricingCalculator(room_type.hotel)
        
        pricing = calculator.calculate_total_price(
            room_type=room_type,
            check_in=serializer.validated_data['check_in'],
            check_out=serializer.validated_data['check_out'],
            num_rooms=serializer.validated_data.get('num_rooms', 1),
            discount_code=serializer.validated_data.get('discount_code')
        )
        
        return Response({
            'success': True,
            'pricing': pricing
        }, status=status.HTTP_200_OK)
    
    except RoomType.DoesNotExist:
        return Response(
            {'error': 'Room type not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def check_availability(request):
    """
    Check if rooms are available for dates
    
    Request body:
    {
        "room_type_id": 1,
        "check_in": "2024-01-10",
        "check_out": "2024-01-15",
        "num_rooms": 2
    }
    """
    serializer = AvailabilityCheckSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        room_type = RoomType.objects.get(id=serializer.validated_data['room_type_id'])
        calculator = PricingCalculator(room_type.hotel)
        
        availability = calculator.check_availability(
            room_type=room_type,
            check_in=serializer.validated_data['check_in'],
            check_out=serializer.validated_data['check_out'],
            num_rooms=serializer.validated_data.get('num_rooms', 1)
        )
        
        return Response({
            'success': True,
            'availability': availability
        }, status=status.HTTP_200_OK)
    
    except RoomType.DoesNotExist:
        return Response(
            {'error': 'Room type not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def get_hotel_occupancy(request, hotel_id):
    """
    Get occupancy details for a hotel
    
    Query Parameters:
    - start_date: Start date (YYYY-MM-DD)
    - end_date: End date (YYYY-MM-DD)
    """
    try:
        hotel = Hotel.objects.get(id=hotel_id)
        
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        
        if not start_date_str or not end_date_str:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
        
        occupancy = OccupancyCalculator.get_hotel_occupancy_summary(
            hotel, start_date, end_date
        )
        
        return Response({
            'success': True,
            'occupancy': occupancy
        }, status=status.HTTP_200_OK)
    
    except Hotel.DoesNotExist:
        return Response(
            {'error': 'Hotel not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


# ============================================
# HTML WEB VIEWS
# ============================================

def hotel_list(request):
    """Hotel listing page with search"""
    
    hotels = (
        Hotel.objects.filter(is_active=True)
        .annotate(min_price=Coalesce(Min('room_types__base_price'), Value(0, output_field=DecimalField())))
        .select_related('city')
        .prefetch_related('images', 'room_types', 'channel_mappings')
    )
    cities = City.objects.all().order_by('name')
    
    # Search filters
    city_id = request.GET.get('city_id')
    if city_id:
        try:
            cid = int(city_id)
            hotels = hotels.filter(city_id=cid)
        except (ValueError, TypeError):
            hotels = hotels.filter(city__name__iexact=city_id)
    
    checkin = request.GET.get('checkin')
    checkout = request.GET.get('checkout')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    star_rating = request.GET.get('star_rating')
    sort = request.GET.get('sort')
    guests = request.GET.get('guests')

    # Basic price range filter
    if price_min:
        hotels = hotels.filter(min_price__gte=price_min)
    if price_max:
        hotels = hotels.filter(min_price__lte=price_max)

    # Star rating filter
    if star_rating:
        hotels = hotels.filter(star_rating=star_rating)

    # Sorting
    if sort == 'price_asc':
        hotels = hotels.order_by('min_price')
    elif sort == 'price_desc':
        hotels = hotels.order_by('-min_price')
    elif sort == 'rating_desc':
        hotels = hotels.order_by('-review_rating')
    elif sort == 'rating_asc':
        hotels = hotels.order_by('review_rating')
    
    availability_errors = {}
    if checkin and checkout:
        for hotel in hotels:
            try:
                hotel.availability_snapshot = get_hotel_availability_snapshot(
                    hotel, checkin, checkout, int(guests or 1)
                )
                hotel.availability_error = None
            except AvailabilityError as exc:
                hotel.availability_snapshot = None
                hotel.availability_error = str(exc)
                availability_errors[hotel.id] = str(exc)
            except Exception:
                hotel.availability_snapshot = None
                hotel.availability_error = "Availability temporarily unavailable"
                availability_errors[hotel.id] = "Availability temporarily unavailable"

    context = {
        'hotels': list(hotels),
        'cities': cities,
        'selected_city': city_id,
        'selected_checkin': checkin,
        'selected_checkout': checkout,
        'selected_price_min': price_min,
        'selected_price_max': price_max,
        'selected_star_rating': star_rating,
        'selected_sort': sort,
        'selected_guests': guests,
        'availability_errors': availability_errors,
    }
    
    return render(request, 'hotels/hotel_list.html', context)


def hotel_detail(request, pk):
    """Hotel detail page"""
    hotel_qs = Hotel.objects.select_related('city').prefetch_related('images', 'room_types', 'channel_mappings')
    hotel = get_object_or_404(hotel_qs, pk=pk, is_active=True)
    today = date.today()
    default_checkin = request.GET.get('checkin') or today.strftime('%Y-%m-%d')
    default_checkout = request.GET.get('checkout') or (today + timedelta(days=1)).strftime('%Y-%m-%d')
    default_guests = request.GET.get('guests') or 1
    default_room_type = request.GET.get('room_type')
    
    try:
        availability_snapshot = get_hotel_availability_snapshot(hotel, default_checkin, default_checkout, int(default_guests or 1))
    except Exception:
        availability_snapshot = None

    context = {
        'hotel': hotel,
        'prefill_checkin': default_checkin,
        'prefill_checkout': default_checkout,
        'prefill_guests': default_guests,
        'prefill_room_type': default_room_type,
        'availability_snapshot': availability_snapshot,
    }
    
    return render(request, 'hotels/hotel_detail.html', context)


@csrf_exempt
def book_hotel(request, pk):
    """Book hotel (POST handler)"""
    hotel_qs = Hotel.objects.prefetch_related('room_types', 'channel_mappings').select_related('city')
    hotel = get_object_or_404(hotel_qs, pk=pk, is_active=True)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f'/login/?next={request.path}')

        room_type_id = request.POST.get('room_type')
        checkin_date = request.POST.get('checkin_date')
        checkout_date = request.POST.get('checkout_date')
        num_rooms = int(request.POST.get('num_rooms', 1))
        guests = int(request.POST.get('num_guests', 1))
        guest_name = request.POST.get('guest_name')
        guest_email = request.POST.get('guest_email')
        guest_phone = request.POST.get('guest_phone')

        try:
            checkin = datetime.strptime(checkin_date, '%Y-%m-%d').date()
            checkout = datetime.strptime(checkout_date, '%Y-%m-%d').date()
        except Exception:
            return render(request, 'hotels/hotel_detail.html', {'hotel': hotel, 'error': 'Invalid dates selected'})

        if checkout <= checkin:
            return render(request, 'hotels/hotel_detail.html', {'hotel': hotel, 'error': 'Check-out must be after check-in'})

        try:
            room_type = hotel.room_types.get(id=room_type_id)
        except RoomType.DoesNotExist:
            return render(request, 'hotels/hotel_detail.html', {'hotel': hotel, 'error': 'Room type not found'})

        hold_minutes = 15
        lock = None
        inventory_channel = hotel.inventory_source
        booking_source = 'external' if hotel.inventory_source == 'external_cm' else 'internal'

        try:
            if hotel.inventory_source == 'external_cm':
                mapping = ChannelManagerRoomMapping.objects.filter(room_type=room_type, is_active=True).first()
                if not mapping:
                    raise InventoryLockError('Channel manager mapping is missing for the selected room.')
                cm_client = ExternalChannelManagerClient(provider=mapping.provider)
                lock_resp = cm_client.lock_inventory(mapping, checkin, checkout, num_rooms, hold_minutes=hold_minutes)
                reference_id = lock_resp.get('lock_id') or f"CM-{uuid.uuid4().hex[:10].upper()}"
                lock = InventoryLock.objects.create(
                    hotel=hotel,
                    room_type=room_type,
                    reference_id=reference_id,
                    lock_id=lock_resp.get('lock_id', reference_id),
                    source='external_cm',
                    provider=mapping.provider,
                    check_in=checkin,
                    check_out=checkout,
                    num_rooms=num_rooms,
                    expires_at=lock_resp.get('expires_at', timezone.now() + timedelta(minutes=hold_minutes)),
                    payload={'mapping_id': mapping.id},
                )
            else:
                internal_service = InternalInventoryService(hotel)
                lock = internal_service.lock_inventory(
                    room_type=room_type,
                    check_in=checkin,
                    check_out=checkout,
                    num_rooms=num_rooms,
                    hold_minutes=hold_minutes,
                )
        except InventoryLockError as exc:
            return render(request, 'hotels/hotel_detail.html', {'hotel': hotel, 'error': str(exc)})

        nights = (checkout - checkin).days
        total = room_type.base_price * nights * num_rooms

        try:
            booking = Booking.objects.create(
                user=request.user,
                booking_type='hotel',
                total_amount=total,
                status='payment_pending',
                customer_name=guest_name or request.user.get_full_name() or request.user.username,
                customer_email=guest_email or request.user.email,
                customer_phone=guest_phone or getattr(request.user, 'phone', ''),
                booking_source=booking_source,
                inventory_channel=inventory_channel,
                lock_id=(lock.lock_id or lock.reference_id) if lock else '',
            )

            if lock:
                lock.booking = booking
                lock.save(update_fields=['booking'])

            HotelBooking.objects.create(
                booking=booking,
                room_type=room_type,
                check_in=checkin,
                check_out=checkout,
                number_of_rooms=num_rooms,
                number_of_adults=guests,
                total_nights=nights,
            )

            # Use the public booking UUID, not the numeric PK, to match URL patterns
            return redirect(f'/bookings/{booking.booking_id}/confirm/')
        except Exception as exc:
            if lock and lock.source == 'internal_cm':
                InternalInventoryService(hotel).release_lock(lock)
            elif lock and lock.source == 'external_cm':
                try:
                    ExternalChannelManagerClient(provider=lock.provider).release_lock(lock.lock_id or lock.reference_id)
                except InventoryLockError:
                    pass
            return render(request, 'hotels/hotel_detail.html', {'hotel': hotel, 'error': str(exc)})

    return redirect(f'/hotels/{pk}/')
