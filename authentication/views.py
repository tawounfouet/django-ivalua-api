from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .forms import EmailAuthenticationForm, UserRegistrationForm


class EmailLoginView(LoginView):
    """
    Login view that uses email for authentication.
    """
    form_class = EmailAuthenticationForm
    template_name = 'authentication/login.html'


class RegisterView(CreateView):
    """
    View for registering a new user with email.
    """
    form_class = UserRegistrationForm
    template_name = 'authentication/register.html'
    success_url = reverse_lazy('login')