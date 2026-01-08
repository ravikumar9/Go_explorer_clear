from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'users'

urlpatterns = [
    # Web UI authentication
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.user_profile, name='profile'),

    # API endpoints
    path('api/profile/', views.UserProfileView.as_view(), name='api-profile'),
]
