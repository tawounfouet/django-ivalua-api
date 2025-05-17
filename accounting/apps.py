from django.apps import AppConfig


class AccountingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounting'
    verbose_name = 'Comptabilité'
    
    def ready(self):
        # Import signals if you have any
        # import accounting.signals
        pass
