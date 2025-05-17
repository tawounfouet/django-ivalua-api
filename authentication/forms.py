from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class EmailAuthenticationForm(AuthenticationForm):
    """
    Authentication form which uses email address instead of username.
    """
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={'autofocus': True}),
        error_messages={
            'required': _('Please enter your email address'),
            'invalid': _('Please enter a valid email address'),
        }
    )
    
    error_messages = {
        'invalid_login': _(
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }


class UserRegistrationForm(UserCreationForm):
    """
    Form for registering a new user account with email.
    """
    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
        error_messages={
            'required': _('Please enter your email address'),
            'invalid': _('Please enter a valid email address'),
        }
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')