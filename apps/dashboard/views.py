from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse


def redirect_dashboard(request):
    return redirect(reverse('dashboard'))


@login_required
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')
