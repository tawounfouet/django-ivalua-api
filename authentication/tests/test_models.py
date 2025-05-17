import pytest
from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from authentication.models import UserProfile
from datetime import timedelta

User = get_user_model()


class UserManagerTests(TestCase):
    """Tests for the custom UserManager."""

    def test_create_user(self):
        """Test creating a regular user with email."""
        email = 'test@example.com'
        user = User.objects.create_user(
            email=email,
            password='testpass123'
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.username)  # Username should be auto-generated
        
        # Test that password is correctly hashed (not stored as plaintext)
        self.assertNotEqual(user.password, 'testpass123')
        self.assertTrue(user.check_password('testpass123'))
        
        # Test that calling create_user with no email raises error
        with self.assertRaises(ValueError):
            User.objects.create_user(email='')

    def test_create_superuser(self):
        """Test creating a superuser."""
        email = 'admin@example.com'
        user = User.objects.create_superuser(
            email=email,
            password='testpass123'
        )
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        
        # Test that passing is_staff=False raises error
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin2@example.com',
                password='testpass123',
                is_staff=False
            )
        
        # Test that passing is_superuser=False raises error
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email='admin3@example.com',
                password='testpass123',
                is_superuser=False
            )


class UserModelTests(TestCase):
    """Tests for the custom User model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_auto_username_generation(self):
        """Test that username is automatically generated from email."""
        # Username should be the part before @ in email
        self.assertEqual(self.user.username, 'test')
        
        # Creating another user with same email prefix should add a suffix
        user2 = User.objects.create_user(
            email='test@anotherdomain.com',
            password='testpass123'
        )
        self.assertEqual(user2.username, 'test1')
        
        # And a third one should increment the suffix
        user3 = User.objects.create_user(
            email='test@thirddomain.com',
            password='testpass123'
        )
        self.assertEqual(user3.username, 'test2')
    
    def test_custom_username(self):
        """Test that a custom username can be provided."""
        user = User.objects.create_user(
            email='custom@example.com',
            username='customusername',
            password='testpass123'
        )
        self.assertEqual(user.username, 'customusername')
    
    def test_email_normalization(self):
        """Test that email addresses are normalized."""
        #email = 'test@EXAMPLE.com'
        email = 'normalization@EXAMPLE.com'  # Utiliser une adresse email unique
        user = User.objects.create_user(email=email, password='testpass123')
        self.assertEqual(user.email, email.lower())
    
    def test_is_locked_property(self):
        """Test the is_locked property."""
        # Initially account should not be locked
        self.assertFalse(self.user.is_locked)
        
        # Lock the account
        self.user.account_locked_until = timezone.now() + timedelta(minutes=30)
        self.user.save()
        
        # Now it should be locked
        self.assertTrue(self.user.is_locked)
        
        # Set lock time in the past
        self.user.account_locked_until = timezone.now() - timedelta(minutes=1)
        self.user.save()
        
        # Now it should not be locked
        self.assertFalse(self.user.is_locked)
    
    def test_increment_failed_logins(self):
        """Test incrementing failed login attempts."""
        self.assertEqual(self.user.failed_login_attempts, 0)
        
        # Increment once
        self.user.increment_failed_logins()
        self.assertEqual(self.user.failed_login_attempts, 1)
        self.assertIsNone(self.user.account_locked_until)
        
        # Increment to threshold
        for _ in range(4):  # Already at 1, so 4 more to reach 5
            self.user.increment_failed_logins()
        
        # Should be locked now
        self.assertEqual(self.user.failed_login_attempts, 5)
        self.assertIsNotNone(self.user.account_locked_until)
        self.assertTrue(self.user.is_locked)
    
    def test_reset_failed_logins(self):
        """Test resetting failed login attempts."""
        # Set up some failed attempts
        self.user.failed_login_attempts = 3
        self.user.account_locked_until = timezone.now() + timedelta(minutes=30)
        self.user.save()
        
        # Reset
        self.user.reset_failed_logins()
        
        # Check results
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertIsNone(self.user.account_locked_until)
    
    def test_lock_unlock_account(self):
        """Test locking and unlocking account."""
        # Lock
        self.user.lock_account(duration_minutes=60)
        
        # Check it's locked
        self.assertTrue(self.user.is_locked)
        
        # Unlock
        self.user.unlock_account()
        
        # Check it's unlocked
        self.assertFalse(self.user.is_locked)
        self.assertIsNone(self.user.account_locked_until)
    
    def test_record_login(self):
        """Test recording a successful login."""
        # Setup
        self.user.failed_login_attempts = 3
        old_last_login = self.user.last_login
        ip = '192.168.1.1'
        
        # Record login
        self.user.record_login(ip_address=ip)
        
        # Check results
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.assertEqual(self.user.last_login_ip, ip)
        #self.assertGreater(self.user.last_login, old_last_login)

        # Vérifier que last_login a été mis à jour
        if old_last_login is None:
            self.assertIsNotNone(self.user.last_login)
        else:
            self.assertGreater(self.user.last_login, old_last_login)


class UserProfileTests(TestCase):
    """Tests for the UserProfile model."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='profile@example.com',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """Test that profile is created automatically when user is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_profile_str_representation(self):
        """Test the string representation of a profile."""
        expected = "profile@example.com's profile"
        self.assertEqual(str(self.user.profile), expected)
    
    def test_profile_update(self):
        """Test updating profile fields."""
        # Update profile
        self.user.profile.bio = "Test biography"
        self.user.profile.city = "Test City"
        self.user.profile.save()
        
        # Refresh from database
        self.user.refresh_from_db()
        
        # Check updates were saved
        self.assertEqual(self.user.profile.bio, "Test biography")
        self.assertEqual(self.user.profile.city, "Test City")
    
    def test_notification_defaults(self):
        """Test default notification settings."""
        self.assertTrue(self.user.profile.notification_email)
        self.assertFalse(self.user.profile.notification_sms)