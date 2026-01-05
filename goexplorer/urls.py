"""
URL configuration for goexplorer project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('', include('core.urls')),
    # Web page routes with unique namespaces
    # Web routes (use each app's native namespace)
    path('hotels/', include(('hotels.urls', 'hotels'), namespace='hotels')),
    path('buses/', include(('buses.urls', 'buses'), namespace='buses')),
    path('packages/', include(('packages.urls', 'packages'), namespace='packages')),
    path('bookings/', include(('bookings.urls', 'bookings'), namespace='bookings')),
    path('payments/', include(('payments.urls', 'payments'), namespace='payments')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('properties/', include(('property_owners.urls', 'property_owners'), namespace='property_owners')),
    # API endpoints with api- prefix and unique namespaces
    path('api/hotels/', include(('hotels.urls', 'hotels'), namespace='hotels-api')),
    path('api/buses/', include(('buses.urls', 'buses'), namespace='buses-api')),
    path('api/packages/', include(('packages.urls', 'packages'), namespace='packages-api')),
    path('api/bookings/', include(('bookings.urls', 'bookings'), namespace='bookings-api')),
    path('api/payments/', include(('payments.urls', 'payments'), namespace='payments-api')),
    path('api/users/', include(('users.urls', 'users'), namespace='users-api')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "GoExplorer Admin"
admin.site.site_title = "GoExplorer Admin Portal"
admin.site.index_title = "Welcome to GoExplorer Administration"
