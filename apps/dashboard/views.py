from django.shortcuts import redirect
from django.urls import reverse


def redirect_admin(request):
    return redirect(reverse('admin:index'))
