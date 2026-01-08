from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import DetailView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.conf import settings
from .models import Booking
import uuid
try:
    import razorpay
except Exception:
    razorpay = None

class BookingListView(APIView):
    renderer_classes = [JSONRenderer, TemplateHTMLRenderer]

    def get(self, request):
        if request.user.is_authenticated:
            queryset = Booking.objects.filter(user=request.user).order_by('-created_at')
        else:
            queryset = Booking.objects.none()

        # When HTML is requested, render the template for browser use
        if getattr(request, 'accepted_renderer', None) and request.accepted_renderer.format == 'html':
            return Response({'object_list': queryset}, template_name='bookings/booking_list.html')

        # Default to JSON response
        data = [
            {
                'booking_id': str(b.booking_id),
                'booking_type': b.booking_type,
                'status': b.status,
                'total_amount': float(b.total_amount),
                'customer_name': b.customer_name,
            }
            for b in queryset
        ]
        return Response(data)

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'

    def get_object(self, queryset=None):
        booking_id = self.kwargs.get('booking_id')
        return get_object_or_404(Booking, booking_id=booking_id, user=self.request.user)

@login_required
def booking_confirmation(request, booking_id):
    """Show booking confirmation and proceed to payment.

    Accepts only UUID booking_id and ensures the booking belongs to the user.
    POST from this page redirects to the payment page.
    """
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if request.method == 'POST':
        return redirect(reverse('bookings:booking-payment', kwargs={'booking_id': booking.booking_id}))

    return render(request, 'bookings/confirmation.html', {
        'booking': booking,
    })


@login_required
def payment_page(request, booking_id):
    """Render the payment page with a Razorpay order (test-friendly).

    If Razorpay credentials are not configured, fall back to a dummy order id so
    the template renders without breaking local flows.
    """
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    razorpay_key = settings.RAZORPAY_KEY_ID or 'rzp_test_dummy_key'
    order_id = f"order_{uuid.uuid4().hex[:20]}"

    # Create real order if keys and SDK are available
    if razorpay and settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            order = client.order.create(data={
                'amount': int(float(booking.total_amount) * 100),
                'currency': 'INR',
                'receipt': str(booking.booking_id),
                'notes': {'booking_id': str(booking.booking_id), 'user_id': str(request.user.id)}
            })
            order_id = order.get('id', order_id)
        except Exception:
            # Keep fallback order_id for non-blocking local runs
            pass

    context = {
        'booking': booking,
        'total_amount': booking.total_amount,
        'base_amount': booking.total_amount,
        'gst_amount': 0,
        'discount_amount': 0,
        'razorpay_key': razorpay_key,
        'order_id': order_id,
    }
    return render(request, 'payments/payment.html', context)


def create_razorpay_order(request):
    # Inform callers to use the dedicated payments endpoints
    return JsonResponse({"status": "error", "message": "Use payments:create-payment-order API"}, status=405)


def verify_payment(request):
    # Inform callers to use the dedicated payments endpoints
    return JsonResponse({"status": "error", "message": "Use payments:verify-payment API"}, status=405)

