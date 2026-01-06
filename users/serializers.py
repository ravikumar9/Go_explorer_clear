from rest_framework import serializers
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer"""
    class Meta:
        model = UserProfile
        fields = ['id', 'gender', 'address', 'city', 'state', 'country', 'pincode']


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'phone', 'profile']
        read_only_fields = ['id', 'username']
