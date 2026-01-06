from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views

app_name = 'users_api'

urlpatterns = [
    path('register/', csrf_exempt(views.RegisterAPIView.as_view()), name='api-register'),
    path('login/', csrf_exempt(views.LoginAPIView.as_view()), name='api-login'),
    path('profile/', views.UserProfileView.as_view(), name='api-profile'),
]
