from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .serializers import (
    UserSerializer, UserDetailSerializer, UserCreateSerializer,
    ChangePasswordSerializer, CustomTokenObtainPairSerializer
)

User = get_user_model()


class IsOwnProfileOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow users to edit their own profile or for admins.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin permissions
        if request.user.is_staff:
            return True
            
        # Instance must be the user's own profile
        return obj.id == request.user.id


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Takes an email and password and returns an access and refresh token.
    """
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management.
    
    Provides CRUD operations for user accounts with appropriate permission controls.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return UserSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserDetailSerializer
    
    def get_permissions(self):
        """
        Set custom permissions for different actions.
        
        - Create: Allow admin users only
        - List: Allow admin users only
        - Retrieve: Allow admin users or the user themselves
        - Update: Allow admin users or the user themselves
        """
        if self.action in ['create', 'list']:
            permission_classes = [permissions.IsAdminUser]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            permission_classes = [IsOwnProfileOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions.
        
        Admin users can see all users, regular users can only see themselves.
        """
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnProfileOrAdmin])
    def change_password(self, request, pk=None):
        """
        Endpoint to change user password.
        
        Args:
            request: HTTP request with old and new passwords
            pk: User primary key
            
        Returns:
            Response: Success or error message
        """
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": _("Incorrect password.")},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(
                {"message": _("Password changed successfully.")},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def activate(self, request, pk=None):
        """
        Activate a user account (admin only).
        
        Args:
            request: HTTP request
            pk: User primary key
            
        Returns:
            Response: Success or error message
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response(
            {"message": _("User activated successfully.")},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def deactivate(self, request, pk=None):
        """
        Deactivate a user account (admin only).
        
        Args:
            request: HTTP request
            pk: User primary key
            
        Returns:
            Response: Success or error message
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(
            {"message": _("User deactivated successfully.")},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def unlock(self, request, pk=None):
        """
        Unlock a user account (admin only).
        
        Args:
            request: HTTP request
            pk: User primary key
            
        Returns:
            Response: Success or error message
        """
        user = self.get_object()
        user.unlock_account()
        return Response(
            {"message": _("User account unlocked successfully.")},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current authenticated user's information.
        
        Returns:
            Response: Current user data
        """
        user = request.user
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """
        Update current authenticated user's information.
        
        Returns:
            Response: Updated user data
        """
        user = request.user
        serializer = UserDetailSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(viewsets.ViewSet):
    """
    API endpoint for user registration.
    
    Allows users to create new accounts without authentication.
    """
    permission_classes = [permissions.AllowAny]
    
    def create(self, request):
        """
        Register a new user.
        
        Args:
            request: HTTP request with user data
            
        Returns:
            Response: Created user data or validation errors
        """
        serializer = UserCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": _("User registered successfully."),
                    "user_id": user.id,
                    "email": user.email
                }, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)