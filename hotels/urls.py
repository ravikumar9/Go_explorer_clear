from django.urls import path
from . import views

app_name = 'hotels'

urlpatterns = [
    # Web pages (for /hotels/ path)
    path('', views.hotel_list, name='hotel_list'),
    path('<int:pk>/', views.hotel_detail, name='hotel_detail'),
    path('<int:pk>/book/', views.book_hotel, name='book_hotel'),
    
    # API endpoints - Listing & Search
    path('api/list/', views.HotelListView.as_view(), name='hotel-list-api'),
    path('api/search/', views.HotelSearchView.as_view(), name='hotel-search-api'),
    path('api/<int:pk>/', views.HotelDetailView.as_view(), name='hotel-detail-api'),
    
    # API endpoints - Pricing & Availability
    path('api/calculate-price/', views.calculate_price, name='calculate-price'),
    path('api/check-availability/', views.check_availability, name='check-availability'),
    path('api/<int:hotel_id>/occupancy/', views.get_hotel_occupancy, name='hotel-occupancy'),
]
