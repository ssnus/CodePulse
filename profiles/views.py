from django.views.generic import DetailView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from .models import Profile, Follow
from .forms import UserUpdateForm, ProfileUpdateForm


class ProfileDetailView(DetailView):
    """Просмотр профиля пользователя"""
    model = User
    template_name = 'profiles/profile.html'
    context_object_name = 'user_profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_queryset(self):
        return User.objects.select_related('profile').prefetch_related('posts__attachments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, user=self.object)
        context['profile'] = profile

        is_following = False
        if self.request.user.is_authenticated and self.request.user != self.object:
            is_following = Follow.objects.filter(
                follower=self.request.user,
                following=self.object
            ).exists()
        context['is_following'] = is_following

        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля текущего пользователя"""
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'profiles/profile_edit.html'

    def get_object(self):
        return self.request.user.profile

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.POST:
            context['u_form'] = UserUpdateForm(self.request.POST, instance=self.request.user)
        else:
            context['u_form'] = UserUpdateForm(instance=self.request.user)

        context['p_form'] = context['form']

        context['title'] = 'Редактирование профиля'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        p_form = self.get_form()

        u_form = UserUpdateForm(request.POST, instance=request.user)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profiles:profile', username=request.user.username)

        return self.render_to_response(self.get_context_data(u_form=u_form))

    def get_success_url(self):
        return reverse_lazy('profiles:profile', kwargs={'username': self.request.user.username})


class FollowToggleView(LoginRequiredMixin, View):
    def post(self, request, username, *args, **kwargs):
        user_to_toggle = get_object_or_404(User, username=username)

        if request.user == user_to_toggle:
            messages.warning(request, "Вы не можете подписаться на самого себя.")
            return redirect('profiles:profile', username=username)

        follow_obj = Follow.objects.filter(
            follower=request.user,
            following=user_to_toggle
        )

        if follow_obj.exists():
            follow_obj.delete()
        else:
            Follow.objects.create(follower=request.user, following=user_to_toggle)


        return redirect('profiles:profile', username=username)