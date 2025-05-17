from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profiles."""
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'date_of_birth', 'address', 'city', 'country', 
            'organization', 'social_linkedin', 'notification_email', 
            'notification_sms'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users with email authentication."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'is_supplier'
        ]
    
    def validate(self, attrs):
        """Validate that passwords match."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": _("Passwords do not match.")})
        
        # Valider que l'email n'est pas déjà pris
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": _("This email address is already in use.")})
            
        return attrs
    
    def create(self, validated_data):
        """Create a new user with encrypted password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for basic user information."""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'department', 'position', 'phone_number', 'language'
        ]
        read_only_fields = ['id']


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for user information including profile."""
    profile = UserProfileSerializer()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name',
            'employee_id', 'department', 'position', 'phone_number',
            'mobile_number', 'is_supplier', 'language', 'profile_picture',
            'profile', 'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def update(self, instance, validated_data):
        """Update user and nested profile."""
        profile_data = validated_data.pop('profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile if data provided
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
            
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Validate that new passwords match."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": _("New passwords do not match.")})
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that accepts email instead of username.
    """
    username_field = User.USERNAME_FIELD
    
    def validate(self, attrs):
        """
        Validate credentials and return token data.
        
        Overrides to add additional user information to the response.
        """
        # Get the token data
        data = super().validate(attrs)
        
        # Add extra user data to response
        user = self.user
        data.update({
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_supplier': user.is_supplier,
            'language': user.language
        })
        
        return data