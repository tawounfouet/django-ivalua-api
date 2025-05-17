from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuthenticationConfig(AppConfig):
    """
    Configuration for the authentication application.
    
    This application provides custom user models and authentication functionality.
    """
    name = 'authentication'
    verbose_name = _('01 - Users')


    
    def ready(self):
        """
        Initialize signals when the app is ready.
        """
        import authentication.signals  # noqa