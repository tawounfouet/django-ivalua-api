from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    for authentication instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model that uses email for authentication instead of username.
    
    This model adds additional fields needed for the Ivalua API application
    and uses email as the primary identifier for authentication.
    
    Attributes:
        employee_id (str): Internal employee identifier
        department (str): Department where the user works
        position (str): Job title or position
        phone_number (str): Contact phone number
        mobile_number (str): Mobile phone number
        is_supplier (bool): Whether this user represents a supplier
        language (str): Preferred language for communications
        last_login_ip (str): IP address of the last login
        failed_login_attempts (int): Count of consecutive failed login attempts
        account_locked_until (datetime): Time until which account is locked
        profile_picture (ImageField): User's profile image
    """
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("username"),
        help_text=_("Optional username for backward compatibility")
    )
    email = models.EmailField(
        unique=True,
        verbose_name=_("email address"),
        help_text=_("Required. Your email address for login"),
        validators=[EmailValidator()]
    )
    
    # Employee information
    employee_id = models.CharField(
        max_length=20, 
        blank=True,
        verbose_name=_("employee ID"),
        help_text=_("Internal employee identifier")
    )
    department = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("department"),
        help_text=_("Department where the user works")
    )
    position = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("position"),
        help_text=_("Job title or position")
    )
    
    # Contact information
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        verbose_name=_("phone number"),
        help_text=_("Contact phone number with country code")
    )
    mobile_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        verbose_name=_("mobile number"),
        help_text=_("Mobile phone number with country code")
    )
    
    # User type
    is_supplier = models.BooleanField(
        default=False,
        verbose_name=_("supplier user"),
        help_text=_("Whether this user represents a supplier")
    )
    
    # Preferences
    LANGUAGE_CHOICES = [
        ('en', _('English')),
        ('fr', _('French')),
        ('es', _('Spanish')),
        ('de', _('German')),
    ]
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name=_("preferred language"),
        help_text=_("Preferred language for communications")
    )
    
    # Security and tracking
    last_login_ip = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name=_("last login IP"),
        help_text=_("IP address of the last login")
    )
    failed_login_attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("failed login attempts"),
        help_text=_("Count of consecutive failed login attempts")
    )
    account_locked_until = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name=_("account locked until"),
        help_text=_("Time until which account is locked")
    )
    
    # Profile picture
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True, 
        blank=True,
        verbose_name=_("profile picture"),
        help_text=_("User's profile image")
    )

    # Additional metadata fields (created_at, updated_at)
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name=_("created at"),
        help_text=_("Date and time when the user was created")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"),
        help_text=_("Date and time when the user was last updated")
    )
    
    # Changer le champ utilisé pour l'authentification
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email est déjà requis par défaut
    
    # Définir le gestionnaire d'utilisateurs personnalisé
    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ['email']

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        """
        Override the save method to handle username generation if not provided.
        """
        if not self.username:
            # Générer un nom d'utilisateur à partir de l'email si non fourni
            base_username = self.email.split('@')[0]
            username = base_username
            suffix = 1
            
            # S'assurer que le nom d'utilisateur est unique
            while User.objects.filter(username=username).exclude(id=self.id).exists():
                username = f"{base_username}{suffix}"
                suffix += 1
                
            self.username = username
            
        super().save(*args, **kwargs)
    
    @property
    def is_locked(self):
        """
        Check if the user account is currently locked.
        
        Returns:
            bool: True if the account is locked, False otherwise
        """
        if self.account_locked_until and timezone.now() < self.account_locked_until:
            return True
        return False
    
    def increment_failed_logins(self, save=True):
        """
        Increment the failed login attempts counter.
        
        If the number of failed attempts exceeds the threshold, lock the account.
        
        Args:
            save (bool): Whether to save the changes immediately
        """
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            # Lock for 30 minutes
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        
        if save:
            self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    def reset_failed_logins(self, save=True):
        """
        Reset the failed login attempts counter and unlock the account.
        
        Args:
            save (bool): Whether to save the changes immediately
        """
        self.failed_login_attempts = 0
        self.account_locked_until = None
        
        if save:
            self.save(update_fields=['failed_login_attempts', 'account_locked_until'])

    def lock_account(self, duration_minutes=30, save=True):
        """
        Lock the user account for the specified duration.
        
        Args:
            duration_minutes (int): Duration in minutes to lock the account
            save (bool): Whether to save the changes immediately
        """
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        
        if save:
            self.save(update_fields=['account_locked_until'])
            
    def unlock_account(self, save=True):
        """
        Unlock the user account.
        
        Args:
            save (bool): Whether to save the changes immediately
        """
        self.account_locked_until = None
        
        if save:
            self.save(update_fields=['account_locked_until'])
    
    def record_login(self, ip_address=None):
        """
        Record a successful login and reset the failed login counter.
        
        Args:
            ip_address (str): The IP address from which the login occurred
        """
        self.last_login = timezone.now()
        if ip_address:
            self.last_login_ip = ip_address
        self.reset_failed_logins(save=False)
        self.save(update_fields=['last_login', 'last_login_ip', 'failed_login_attempts', 'account_locked_until'])


class UserProfile(models.Model):
    """
    Extended profile information for users.
    
    This model contains additional profile data that is not essential 
    for user authentication but may be needed for application functionality.
    
    Attributes:
        user (User): Associated user
        bio (str): Short biography or description
        date_of_birth (date): User's birth date
        address (str): User's address
        city (str): User's city
        country (str): User's country
        organization (str): User's organization or company
        social_linkedin (str): LinkedIn profile URL
        notification_email (bool): Whether to receive emails for notifications
        notification_sms (bool): Whether to receive SMS for notifications
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_("user"),
        help_text=_("User this profile belongs to")
    )
    bio = models.TextField(
        blank=True,
        verbose_name=_("biography"),
        help_text=_("Short biography or description")
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("date of birth"),
        help_text=_("User's birth date")
    )
    address = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name=_("address"),
        help_text=_("User's address")
    )
    city = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("city"),
        help_text=_("User's city")
    )
    country = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("country"),
        help_text=_("User's country")
    )
    organization = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name=_("organization"),
        help_text=_("User's organization or company")
    )
    social_linkedin = models.URLField(
        blank=True,
        verbose_name=_("LinkedIn"),
        help_text=_("LinkedIn profile URL")
    )
    
    # Notification preferences
    notification_email = models.BooleanField(
        default=True,
        verbose_name=_("email notifications"),
        help_text=_("Whether to receive emails for notifications")
    )
    notification_sms = models.BooleanField(
        default=False,
        verbose_name=_("SMS notifications"),
        help_text=_("Whether to receive SMS for notifications")
    )

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")
        ordering = ['user__email']

    def __str__(self):
        return f"{self.user.email}'s profile"


# Signal pour créer automatiquement un profil pour chaque nouvel utilisateur
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a user profile when a new user is created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal handler to save a user profile when the user is saved.
    """
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)