from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    """Home page view, redirects to dashboard if authenticated"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')