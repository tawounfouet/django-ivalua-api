from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, AdminPasswordChangeForm
from django.utils.html import format_html
from django.urls import reverse, path
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.shortcuts import render
from django import forms

from .models import User, UserProfile


class AdvancedUserCreationForm(UserCreationForm):
    """Form for creating new users in admin with additional fields."""
    is_supplier = forms.BooleanField(
        label=_("Supplier account"),
        required=False,
        help_text=_("Designates whether this user is a supplier. Supplier accounts have limited access.")
    )
    is_staff = forms.BooleanField(
        label=_("Staff status"),
        required=False,
        help_text=_("Designates whether the user can log into this admin site.")
    )
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'is_supplier', 'is_staff')


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profiles."""
    model = UserProfile
    can_delete = False
    verbose_name = _("Profile")
    verbose_name_plural = _("Profile")
    fieldsets = (
        (_('Personal Information'), {
            'fields': ('bio', 'date_of_birth', 'organization')
        }),
        (_('Contact Information'), {
            'fields': ('address', 'city', 'country')
        }),
        (_('Social Media'), {
            'fields': ('social_linkedin',)
        }),
        (_('Notification Preferences'), {
            'fields': ('notification_email', 'notification_sms')
        }),
    )


class SendEmailForm(forms.Form):
    """Form for sending emails to selected users."""
    subject = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'size': '40'})
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 60})
    )
    send_to_inactive = forms.BooleanField(
        required=False,
        help_text=_("Send to inactive users as well")
    )


class ActivityStatusFilter(admin.SimpleListFilter):
    """Custom filter for user activity status."""
    title = _('Activity Status')
    parameter_name = 'activity_status'

    def lookups(self, request, model_admin):
        return (
            ('active', _('Active in last 30 days')),
            ('inactive', _('Inactive for 30+ days')),
            ('never', _('Never logged in')),
        )

    def queryset(self, request, queryset):
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        
        if self.value() == 'active':
            return queryset.filter(last_login__gte=thirty_days_ago)
        elif self.value() == 'inactive':
            return queryset.filter(last_login__lt=thirty_days_ago).exclude(last_login__isnull=True)
        elif self.value() == 'never':
            return queryset.filter(last_login__isnull=True)
        return queryset


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model with email authentication."""
    add_form = AdvancedUserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'username')}),
        (_('Employee info'), {
            'fields': ('employee_id', 'department', 'position'),
            'classes': ('collapse',) if not ('is_supplier', False) else tuple()
        }),
        (_('Contact info'), {'fields': ('phone_number', 'mobile_number')}),
        (_('Preferences'), {'fields': ('language', 'profile_picture')}),
        (_('Security'), {
            'fields': ('last_login_ip', 'failed_login_attempts', 'account_locked_until'),
            'classes': ('collapse',),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_supplier', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_supplier', 'is_staff'),
        }),
    )
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at', 'account_status')
    list_display = ('email', 'full_name', 'account_type', 'account_status', 'department', 'last_login_display')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_supplier', ActivityStatusFilter, 'groups', 'department')
    search_fields = ('email', 'first_name', 'last_name', 'username', 'employee_id', 'profile__organization')
    ordering = ('email',)
    inlines = [UserProfileInline]
    actions = [
        'unlock_accounts', 
        'activate_accounts', 
        'deactivate_accounts', 
        'reset_failed_login_attempts',
        'send_email_to_users'
    ]
    date_hierarchy = 'date_joined'
    list_per_page = 25
    save_on_top = True
    
    def get_urls(self):
        """Add custom URLs for admin actions."""
        urls = super().get_urls()
        custom_urls = [
            path(
                'send-email/',
                self.admin_site.admin_view(self.send_email_view),
                name='auth_user_send_email',
            ),
        ]
        return custom_urls + urls
    
    def full_name(self, obj):
        """Display full name or indicate it's missing."""
        name = obj.get_full_name()
        if name:
            return name
        return format_html('<span style="color:#999">{}</span>', _("Not provided"))
    full_name.short_description = _("Full Name")
    full_name.admin_order_field = 'first_name'
    
    def account_type(self, obj):
        """Display the type of account with appropriate styling."""
        if obj.is_superuser:
            return format_html('<span style="color:red; font-weight:bold">{}</span>', _("Superuser"))
        elif obj.is_staff:
            return format_html('<span style="color:green">{}</span>', _("Staff"))
        elif obj.is_supplier:
            return format_html('<span style="color:orange">{}</span>', _("Supplier"))
        else:
            return _("User")
    account_type.short_description = _("Type")
    
    def account_status(self, obj):
        """Display account status with appropriate icon and color."""
        if not obj.is_active:
            return format_html('<span style="color:red">❌ {}</span>', _("Inactive"))
        elif obj.is_locked:
            until = obj.account_locked_until.strftime("%Y-%m-%d %H:%M") if obj.account_locked_until else ""
            return format_html('<span style="color:orange">🔒 {}{}</span>', 
                              _("Locked"), f" ({until})" if until else "")
        else:
            return format_html('<span style="color:green">✓ {}</span>', _("Active"))
    account_status.short_description = _("Status")
    
    def last_login_display(self, obj):
        """Display last login with appropriate formatting based on recency."""
        if not obj.last_login:
            return format_html('<span style="color:#999">{}</span>', _("Never"))
        
        days_ago = (timezone.now() - obj.last_login).days
        if days_ago < 7:
            return format_html('<span style="color:green">{}</span>', obj.last_login.strftime("%Y-%m-%d %H:%M"))
        elif days_ago < 30:
            return format_html('<span style="color:orange">{}</span>', obj.last_login.strftime("%Y-%m-%d %H:%M"))
        else:
            return format_html('<span style="color:red">{}</span>', obj.last_login.strftime("%Y-%m-%d %H:%M"))
    last_login_display.short_description = _("Last Login")
    last_login_display.admin_order_field = 'last_login'
    
    def get_queryset(self, request):
        """Optimize queryset for admin views."""
        return super().get_queryset(request).select_related('profile')
    
    def get_fieldsets(self, request, obj=None):
        """Adjust fieldsets based on user type."""
        fieldsets = super().get_fieldsets(request, obj)
        if obj and obj.is_supplier:
            # Customize fieldsets for supplier accounts
            for i, (name, options) in enumerate(fieldsets):
                if name == _('Employee info'):
                    options['classes'] = ('collapse',)
                elif name == _('Permissions'):
                    # Limit permission options for suppliers
                    fields = list(options['fields'])
                    if 'is_staff' in fields and 'is_superuser' in fields:
                        fields = [f for f in fields if f not in ('is_staff', 'is_superuser')]
                        options['fields'] = tuple(fields)
        return fieldsets
    
    def unlock_accounts(self, request, queryset):
        """Admin action to unlock selected user accounts."""
        count = 0
        for user in queryset:
            if user.is_locked:
                user.unlock_account()
                count += 1
        if count > 0:
            self.message_user(request, _("%(count)d accounts have been unlocked.") % {'count': count})
        else:
            self.message_user(request, _("No accounts were locked."))
    unlock_accounts.short_description = _("Unlock selected accounts")
    
    def activate_accounts(self, request, queryset):
        """Admin action to activate selected user accounts."""
        updated = queryset.update(is_active=True)
        self.message_user(request, _("%(count)d accounts have been activated.") % {'count': updated})
    activate_accounts.short_description = _("Activate selected accounts")
    
    def deactivate_accounts(self, request, queryset):
        """Admin action to deactivate selected user accounts."""
        if queryset.filter(is_superuser=True).exists():
            self.message_user(request, _("Cannot deactivate superuser accounts."), level=messages.ERROR)
            return
        updated = queryset.filter(~Q(pk=request.user.pk)).update(is_active=False)
        if updated < queryset.count():
            self.message_user(
                request, 
                _("%(updated)d accounts have been deactivated. Skipped your own account and superusers.") % 
                {'updated': updated}
            )
        else:
            self.message_user(request, _("%(count)d accounts have been deactivated.") % {'count': updated})
    deactivate_accounts.short_description = _("Deactivate selected accounts")
    
    def reset_failed_login_attempts(self, request, queryset):
        """Admin action to reset failed login attempts for selected users."""
        updated = queryset.update(failed_login_attempts=0, account_locked_until=None)
        self.message_user(request, _("Reset failed login attempts for %(count)d users.") % {'count': updated})
    reset_failed_login_attempts.short_description = _("Reset failed login attempts")
    
    def send_email_to_users(self, request, queryset):
        """Admin action to send an email to selected users."""
        return HttpResponseRedirect(reverse('admin:auth_user_send_email') + 
                                    f'?ids={",".join(str(pk) for pk in queryset.values_list("pk", flat=True))}')
    send_email_to_users.short_description = _("Send email to selected users")
    
    def send_email_view(self, request):
        """View for sending emails to selected users."""
        user_ids = request.GET.get('ids', '').split(',')
        users = User.objects.filter(pk__in=user_ids)
        
        if request.method == 'POST':
            form = SendEmailForm(request.POST)
            if form.is_valid():
                subject = form.cleaned_data['subject']
                message = form.cleaned_data['message']
                send_to_inactive = form.cleaned_data['send_to_inactive']
                
                recipients = users if send_to_inactive else users.filter(is_active=True)
                recipient_emails = [u.email for u in recipients]
                
                # Here you would implement the actual email sending
                # For now, we'll just show a success message
                self.message_user(
                    request, 
                    _("Email with subject '%(subject)s' would be sent to %(count)d users.") % 
                    {'subject': subject, 'count': len(recipient_emails)}
                )
                return HttpResponseRedirect(reverse('admin:authentication_user_changelist'))
        else:
            form = SendEmailForm()
        
        context = {
            'title': _('Send Email to Users'),
            'form': form,
            'users': users,
            'opts': self.model._meta,
            'original': _('Send Email'),
        }
        return render(request, 'admin/auth/user/send_email.html', context)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for user profiles."""
    list_display = ('user_link', 'organization', 'city', 'country')
    list_filter = ('notification_email', 'notification_sms', 'country')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'organization', 'city', 'country')
    fieldsets = (
        (None, {'fields': ('user',)}),
        (_('Profile Information'), {
            'fields': ('bio', 'date_of_birth', 'address', 'city', 'country', 'organization')
        }),
        (_('Social Media'), {
            'fields': ('social_linkedin',)
        }),
        (_('Preferences'), {
            'fields': ('notification_email', 'notification_sms')
        }),
    )
    readonly_fields = ('user',)
    
    def user_link(self, obj):
        """Create a link to the user."""
        return format_html(
            '<a href="{}">{}</a>',
            reverse('admin:authentication_user_change', args=[obj.user.id]),
            obj.user.email
        )
    user_link.short_description = _("User")
    user_link.admin_order_field = 'user__email'