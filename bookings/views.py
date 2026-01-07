from uuid import UUID  # Import UUID for validation
from django.shortcuts import render, get_object_or_404, redirect  # Import required functions from Django
from django.contrib.auth.decorators import login_required
from django.conf import settings  # Import settings for access to Razorpay key

@login_required
def booking_confirmation(request, booking_id):
    """Booking confirmation page with payment"""
    # Validate the booking_id to ensure it's a valid UUID
    try:
        UUID(booking_id)  # This will raise a ValueError if booking_id is not a valid UUID
    except ValueError:
        return render(request, '404.html', status=404)  # You can return a 404 page or an appropriate error message

    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)

    if request.method == 'POST':
        return redirect('bookings:payment', booking_id=booking_id)

    context = {
        'booking': booking,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
    }
    return render(request, 'bookings/confirmation.html', context)

