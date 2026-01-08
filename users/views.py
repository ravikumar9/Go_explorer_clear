from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import User, UserProfile
from .serializers import UserSerializer
from django import forms


class UserRegistrationForm(forms.ModelForm):
    """User registration form"""
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone']
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")
        
        if User.objects.filter(email=cleaned_data.get('email')).exists():
            raise forms.ValidationError("Email already registered")

        # Phone is mandatory: numeric and valid length
        phone = cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Mobile number is required")
        if not str(phone).isdigit():
            raise forms.ValidationError("Mobile number must be numeric")
        if len(str(phone)) < 10 or len(str(phone)) > 15:
            raise forms.ValidationError("Mobile number must be 10-15 digits long")
        
        return cleaned_data


class UserLoginForm(forms.Form):
    """User login form"""
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


@csrf_protect
@require_http_methods(["GET", "POST"])
def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create user with email as username
                user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    phone=form.cleaned_data.get('phone', '')
                )
                # Create user profile
                UserProfile.objects.create(user=user)
            
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/register.html', {'form': form})


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.email}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid email or password')
    else:
        form = UserLoginForm()
    
    return render(request, 'users/login.html', {'form': form})


@login_required(login_url='users:login')
@require_http_methods(["POST"])
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(APIView):
    """API endpoint for user registration"""
    
    def post(self, request):
        """Register a new user"""
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        phone = request.data.get('phone', '')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    phone=phone
                )
                UserProfile.objects.create(user=user)
            
            return Response(
                {'message': 'User registered successfully', 'user_id': user.id},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    """API endpoint for user login"""
    
    def post(self, request):
        """Login user"""
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return Response(
                {'message': 'Login successful', 'user': UserSerializer(user).data},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'error': 'Invalid email or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )
