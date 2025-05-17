from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_login_failed
from .models import User


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    Signal handler for successful user logins.
    
    Records the login time and IP address, and resets failed login counters.
    
    Args:
        sender: The class of the user that just logged in
        request: The current request
        user: The user instance that just logged in
    """
    if request:
        ip_address = request.META.get('REMOTE_ADDR')
        user.record_login(ip_address)


@receiver(user_login_failed)
def user_login_failed_handler(sender, credentials, request, **kwargs):
    """
    Signal handler for failed login attempts.
    
    Increments the failed login counter for the user, if the user exists.
    
    Args:
        sender: The class that failed login
        credentials: The credentials that were used to attempt to log in
        request: The current request
    """
    username = credentials.get('username', '')
    if username:
        try:
            # Pour l'authentification par email, username est en fait l'email
            user = User.objects.get(email=username)
            user.increment_failed_logins()
        except User.DoesNotExist:
            # Essayer avec le username si l'email n'est pas trouvé
            try:
                user = User.objects.get(username=username)
                user.increment_failed_logins()
            except User.DoesNotExist:
                # Aucun utilisateur trouvé avec cet email ou username
                pass


# Les signaux pour la création automatique de profil utilisateur sont déjà
# définis dans le fichier models.py, donc nous n'avons pas besoin de les
# répéter ici. Ces signaux sont :
# 
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)
# 
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     try:
#         instance.profile.save()
#     except UserProfile.DoesNotExist:
#         UserProfile.objects.create(user=instance)