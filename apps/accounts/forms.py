from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form that allows users to authenticate with either a username or an email.
    """
    username = forms.CharField(
        label=_("Username or Email"),
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Enter your username or email'),
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': _('Enter your password')
        })
    )

    def clean(self):
        username_or_email = self.cleaned_data.get('username') or self.data.get('username')
        password = self.cleaned_data.get('password') or self.data.get('password')

        print(f"Attempting authentication with: {username_or_email}")  # Debug

        if not username_or_email or not password:
            raise ValidationError(_("Both username/email and password are required."), code='required')

        user = None

        # Check if input is an email
        if '@' in username_or_email:
            user = User.objects.filter(email=username_or_email).first()
        else:
            user = User.objects.filter(username=username_or_email).first()

        if user:
            self.user_cache = authenticate(self.request, username=user.username, password=password)
        else:
            self.user_cache = None

        if self.user_cache is None:
            raise ValidationError(
                _("Please enter a correct username/email and password. Note that both fields may be case-sensitive."),
                code='invalid_login',
            )

        if not self.user_cache.is_active:
            raise ValidationError(_("This account is inactive."), code='inactive')

        if not (self.user_cache.is_staff or self.user_cache.is_superuser):
            raise ValidationError(_("You don't have permission to access the admin site."), code='no_permission')

        return self.cleaned_data
