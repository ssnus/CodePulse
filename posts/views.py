from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home_view(request):
    """Главная страница"""
    if request.user.is_authenticated:
        return render(request, 'posts/home.html', {'title': 'Лента'})
    else:
        return render(request, 'posts/welcome.html', {'title': 'Добро пожаловать'})