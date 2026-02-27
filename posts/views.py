from django.views.generic import ListView, DetailView, CreateView, DeleteView, View
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.db.models import Q, Exists, OuterRef
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Post, Comment, Attachment
from profiles.models import Follow
from .forms import PostForm, CommentForm


class HomeView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts/home.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        following_subquery = Follow.objects.filter(
            follower=self.request.user,
            following=OuterRef('author')
        )

        return Post.objects.select_related(
            'author', 'author__profile'
        ).prefetch_related('comments__author').annotate(
            is_following=Exists(following_subquery)
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        context['title'] = 'Лента'
        return context

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            files = request.FILES.getlist('attachments')
            if len(files) > 5:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse(
                        {
                            'success': False,
                            'errors': {'attachments': ['Можно прикрепить не более 5 файлов.']},
                        },
                        status=400,
                    )
                return redirect('posts:home')

            for f in files:
                Attachment.objects.create(post=post, file=f)

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                post_html = render_to_string(
                    'posts/_post_card.html',
                    {'post': post, 'request': request}
                )
                return JsonResponse({
                    'success': True,
                    'html': post_html,
                })
            return redirect('posts:home')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
            return JsonResponse({'success': False, 'errors': errors}, status=400)

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

class SearchView(ListView):
    template_name = 'posts/search_results.html'
    context_object_name = 'posts'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip().lower()
        if not query:
            return Post.objects.none()

        return Post.objects.filter(
            content_lower__contains=query
        ).select_related('author', 'author__profile')

    def dispatch(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            queryset = self.get_queryset()
            query = request.GET.get('q', '').strip().lower()

            users = User.objects.filter(
                Q(username__icontains=query) | Q(first_name__icontains=query)
            ).select_related('profile')[:3]

            results = []
            for u in users:
                results.append({
                    'type': 'Пользователь',
                    'title': f"@{u.username}",
                    'url': reverse('profiles:profile', kwargs={'username': u.username}),  # ✅ reverse
                    'icon': 'bi-person'
                })

            for p in queryset[:3]:
                content_preview = p.content[:40] + '...' if p.content else ''
                results.append({
                    'type': 'Пост',
                    'title': content_preview,
                    'url': reverse('posts:post_detail', kwargs={'pk': p.pk}),  # ✅ reverse
                    'icon': 'bi-file-post'
                })

            return JsonResponse({'results': results})

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip().lower()  # ✅ .lower()

        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query)
        ).select_related('profile')[:3]

        context['query'] = query
        context['users'] = users
        context['title'] = f'Поиск: {query}'
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('posts:home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)

        if 'attachments' in self.request.FILES:
            for f in self.request.FILES.getlist('attachments'):
                Attachment.objects.create(post=self.object, file=f)

        return response


class PostDetailView(DetailView, FormMixin):
    model = Post
    template_name = 'posts/post_detail.html'
    form_class = CommentForm
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.select_related('author', 'author__profile').prefetch_related('comments__author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['comments'] = self.object.comments.order_by('created_at')
        context['title'] = f'Пост от {self.object.author.username}'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.author = request.user
            comment.save()
            return redirect('posts:post_detail', pk=self.object.pk)
        return self.render_to_response(self.get_context_data(form=form))


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('posts:home')

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Пост успешно удалён!')
        return super().delete(request, *args, **kwargs)



@login_required
def post_like_toggle(request, pk):
    post = get_object_or_404(Post, pk=pk)
    liked = request.user in post.likes.all()

    if liked:
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'total_likes': post.likes.count()})

    next_url = request.POST.get('next') or request.GET.get('next') or 'posts:home'
    return redirect(next_url)

@login_required
def post_comment_create(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

    next_url = request.POST.get('next') or 'posts:home'
    return redirect(next_url)