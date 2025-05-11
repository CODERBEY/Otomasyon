from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Email veya sifre hatali.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')