from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authentication backend which allows users to authenticate with their email address.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user based on email address as the user identifier.
        """
        try:
            # Get the user by email (username is actually the email in the form)
            user = User.objects.get(email=username)
            
            # Check the password
            if user.check_password(password):
                return user
                
            # Check if account is locked
            if hasattr(user, 'is_locked') and user.is_locked():
                return None
                
        except User.DoesNotExist:
            # If user doesn't exist by email, try traditional username login as fallback
            if '@' not in username:  # Only attempt username login if not in email format
                try:
                    user = User.objects.get(username=username)
                    if user.check_password(password):
                        return user
                except User.DoesNotExist:
                    pass
            
            # Run the default password hasher once to reduce timing
            # attacks targeting user enumeration
            User().set_password(password)
            
        return None