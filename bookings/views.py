from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from .models import Booking

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user).order_by('-created_at')

class BookingDetailView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'

    def get_object(self, queryset=None):
        booking_id = self.kwargs.get('booking_id')
        return get_object_or_404(Booking, booking_id=booking_id, user=self.request.user)

# --- Additional booking endpoints required by urls ---
def booking_confirmation(request, booking_id):
    return HttpResponse("Booking confirmation placeholder")

def payment_page(request, booking_id):
    return HttpResponse("Payment page placeholder")

def create_razorpay_order(request):
    return JsonResponse({"status": "ok", "message": "order created (placeholder)"})

def verify_payment(request):
    return JsonResponse({"status": "ok", "message": "payment verified (placeholder)"})

