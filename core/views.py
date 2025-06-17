from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    """Home page view - shows welcome page for unauthenticated users"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/welcome.html')

def welcome(request):
    """Welcome page showcasing ResourcePro features"""
    return render(request, 'core/welcome.html')