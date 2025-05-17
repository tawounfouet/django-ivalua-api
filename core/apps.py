# apps/core/apps.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoreConfig(AppConfig):
    """
    Configuration for the core application.
    
    This application contains base models and shared functionality.
    """
    # Changez cette ligne
    name = 'core'  # Au lieu de 'apps.core'
    verbose_name = _('Core')  # S'il y a cette ligne, gardez-la
    
    def ready(self):
        """
        Perform initialization tasks when the app is ready.
        """
        # Import signal handlers
        # Commentez ou supprimez cette ligne si vous n'avez pas de fichier signals.py
        import core.signals  # noqa