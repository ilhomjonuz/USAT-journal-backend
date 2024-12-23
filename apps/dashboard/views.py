from django.shortcuts import render, redirect
from django.urls import reverse


def redirect_admin(request):
    return redirect(reverse('admin:index'))
