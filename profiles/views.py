from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, Follow


@login_required
def profile_view(request, username):
    """Просмотр профиля пользователя"""
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    # Проверяем, подписан ли текущий пользователь на этого пользователя
    is_following = False
    if request.user.is_authenticated and request.user != user:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()

    context = {
        'user_profile': user,
        'profile': profile,
        'is_following': is_following,
    }
    return render(request, 'profiles/profile.html', context)


@login_required
def profile_edit_view(request):
    """Редактирование профиля текущего пользователя"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваш профиль был успешно обновлён!')
            return redirect('profile', username=request.user.username)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title': 'Редактирование профиля'
    }
    return render(request, 'profiles/profile_edit.html', context)