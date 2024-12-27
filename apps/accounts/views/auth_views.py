from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.shortcuts import redirect


class CustomLoginView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    next_page = reverse_lazy('dashboard')

    def form_valid(self, form):
        messages.success(self.request, _('Welcome back! You have successfully logged in.'))
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, _('Invalid username or password.'))
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = 'login'
    http_method_names = ['post']

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST':
            messages.success(request, _('You have been successfully logged out.'))
            return super().dispatch(request, *args, **kwargs)
        return redirect('dashboard')
