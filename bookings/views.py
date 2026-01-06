from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .serializers import BookingSerializer
from .models import Booking
import razorpay
from django.conf import settings
import json
from notifications.services import EmailService, WhatsAppService, SMSService


class BookingListView(generics.ListAPIView):
    """List all user bookings"""
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class BookingDetailView(generics.RetrieveAPIView):
    """Get booking details"""
    permission_classes = [IsAuthenticated]
    lookup_field = 'booking_id'
    serializer_class = BookingSerializer
    
    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


@login_required
def booking_confirmation(request, booking_id):
    """Booking confirmation page with payment"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    if request.method == 'POST':
        return redirect('bookings:payment', booking_id=booking_id)
    
    context = {
        'booking': booking,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'bookings/confirmation.html', context)


@login_required
def payment_page(request, booking_id):
    """Payment processing page"""
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    context = {
        'booking': booking,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'payments/payment.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_razorpay_order(request):
    """Create Razorpay order"""
    booking_id = request.data.get('booking_id')
    amount = request.data.get('amount')
    
    try:
        booking = Booking.objects.get(booking_id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    order_data = {
        'amount': int(float(amount) * 100),
        'currency': 'INR',
        'receipt': str(booking.booking_id),
        'notes': {
            'booking_id': str(booking.booking_id),
            'user_id': str(request.user.id)
        }
    }
    
    order = client.order.create(data=order_data)
    
    return Response({
        'order_id': order['id'],
        'amount': amount,
        'currency': 'INR',
        'key': settings.RAZORPAY_KEY_ID
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """Verify Razorpay payment"""
    razorpay_order_id = request.data.get('razorpay_order_id')
    razorpay_payment_id = request.data.get('razorpay_payment_id')
    razorpay_signature = request.data.get('razorpay_signature')
    booking_id = request.data.get('booking_id')
    
    import hmac
    import hashlib
    
    message = f"{razorpay_order_id}|{razorpay_payment_id}"
    generated_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    try:
        booking = Booking.objects.get(booking_id=booking_id, user=request.user)
        
        if generated_signature == razorpay_signature:
            from hotels.channel_manager_service import finalize_booking_after_payment
            
            booking = finalize_booking_after_payment(booking, payment_reference=razorpay_payment_id)
            
            # Send booking confirmation notifications
            try:
                booking_data = {
                    'booking_id': str(booking.booking_id),
                    'booking_type': 'Hotel',
                    'property_name': booking.hotel.name if booking.hotel else 'Hotel',
                    'booking_date': f"{booking.check_in} to {booking.check_out}",
                    'price': booking.total_cost,
                    'status': 'Confirmed'
                }
                
                # Send Email
                EmailService.send_booking_confirmation(request.user, booking_data)
                
                # Send SMS (if phone available)
                if request.user.phone:
                    SMSService.send_booking_confirmation(request.user, booking_data)
                
                # Send WhatsApp (if integrated)
                try:
                    WhatsAppService.send_booking_confirmation(request.user, booking_data)
                except:
                    pass  # WhatsApp optional
                    
            except Exception as e:
                print(f"Notification error: {e}")
                pass  # Don't fail booking if notification fails
            
            return Response({
                'status': 'success',
                'message': 'Payment verified and booking confirmed',
                'booking_id': str(booking.booking_id)
            })
        else:
            return Response({
                'status': 'failed',
                'message': 'Invalid signature'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
