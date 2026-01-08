from django.urls import path
from .views import BookingListView, BookingDetailView  # Import classes explicitly
from . import views  # Still import views for other view functions
app_name = 'bookings'

urlpatterns = [
    path('', BookingListView.as_view(), name='booking-list'),
    path('<uuid:booking_id>/', BookingDetailView.as_view(), name='booking-detail'),
    path('<uuid:booking_id>/confirm/', views.booking_confirmation, name='booking-confirm'),
    path('<uuid:booking_id>/payment/', views.payment_page, name='booking-payment'),
    path('api/create-order/', views.create_razorpay_order, name='create-order'),
    path('api/verify-payment/', views.verify_payment, name='verify-payment'),
]

