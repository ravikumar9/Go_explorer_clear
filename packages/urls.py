from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    # Web routes
    path('', views.package_list, name='package_list'),
    path('<int:package_id>/', views.package_detail, name='package_detail'),
    path('<int:package_id>/book/', views.book_package, name='book_package'),
    
    # API routes
    path('api/', views.PackageListView.as_view(), name='package-list'),
    # Legacy/shortcut route so both /api/packages/search/ and /api/packages/api/search/ work
    path('search/', views.PackageSearchView.as_view(), name='package-search-short'),
    path('api/search/', views.PackageSearchView.as_view(), name='package-search'),
    path('api/<int:pk>/', views.PackageDetailView.as_view(), name='package-detail'),
]
