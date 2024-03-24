from django.shortcuts import redirect, render
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User,Group


def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/profile')
        else:
            message = 'enter the correct username and password'
            return render(request, 'login.html', {"message":message})
    return render(request, 'login.html')

def profile(request):
    user = request.user 
    post = "no one"
    if user.is_authenticated:
        if user.groups.filter(name='teacher').exists():
            post = "teacher"
        return render(request, 'profile.html', {"post":post})
    else:
        return redirect('/login_view')

def logout_view(request):
    logout(request)
    return redirect('/login_view')