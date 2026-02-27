from django.views.generic import FormView, RedirectView
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect

from .forms import UserRegisterForm, UserLoginForm


class RegisterView(FormView):
    """Регистрация нового пользователя"""
    template_name = 'accounts/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Вы уже авторизованы.')
            return redirect('posts:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'Аккаунт {username} создан успешно! Теперь вы можете войти.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context


class LoginView(FormView):
    """Вход пользователя"""
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('posts:home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Вы уже авторизованы.')
            return redirect('posts:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, f'Добро пожаловать, {username}!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Неверное имя пользователя или пароль.')
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход'
        return context


class LogoutView(RedirectView):
    """Выход пользователя"""
    url = reverse_lazy('posts:home')

    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Вы успешно вышли из системы.')
        return super().get(request, *args, **kwargs)