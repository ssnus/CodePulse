from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Post, Comment, Attachment
from .forms import PostForm, CommentForm


def home_view(request):
    """Главная страница (лента новостей)"""
    if request.user.is_authenticated:
        posts = (
            Post.objects.select_related('author', 'author__profile')
            .prefetch_related('comments__author')
            .all()
            .order_by('-created_at')[:20]
        )

        # Форма для создания поста
        if request.method == 'POST':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                form = PostForm(request.POST, request.FILES)
                if form.is_valid():
                    post = form.save(commit=False)
                    post.author = request.user
                    post.save()

                    files_saved = 0
                    if 'attachments' in request.FILES:
                        for f in request.FILES.getlist('attachments'):
                            Attachment.objects.create(post=post, file=f)
                            files_saved += 1

                    return JsonResponse({
                        'success': True,
                        'message': f'Пост успешно опубликован! ({files_saved} файлов)',
                        'redirect_url': reverse('home')
                    })
                else:
                    errors = {}
                    for field, error_list in form.errors.items():
                        errors[field] = [str(e) for e in error_list]
                    return JsonResponse({
                        'success': False,
                        'errors': errors
                    }, status=400)
            else:
                form = PostForm(request.POST, request.FILES)
                if form.is_valid():
                    post = form.save(commit=False)
                    post.author = request.user
                    post.save()

                    if 'attachments' in request.FILES:
                        for f in request.FILES.getlist('attachments'):
                            Attachment.objects.create(post=post, file=f)

                    messages.success(request, 'Пост успешно опубликован!')
                    return redirect('home')
        else:
            form = PostForm()

        context = {
            'posts': posts,
            'form': form,
            'title': 'Лента'
        }
        return render(request, 'posts/home.html', context)
    else:
        return render(request, 'posts/welcome.html', {'title': 'Добро пожаловать'})


@login_required
def post_create_view(request):
    """Создание нового поста"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            if 'attachments' in request.FILES:
                for f in request.FILES.getlist('attachments'):
                    Attachment.objects.create(post=post, file=f)

            messages.success(request, 'Пост успешно опубликован!')
            return redirect('home')
        else:
            print("ОШИБКИ ФОРМЫ:", form.errors.as_data())
    else:
        form = PostForm()

    context = {
        'form': form,
        'title': 'Создать пост'
    }
    return render(request, 'posts/post_form.html', context)


@login_required
def post_delete_view(request, pk):
    """Удаление поста"""
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        messages.error(request, 'Вы не можете удалить этот пост!')
        return redirect('home')

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Пост успешно удалён!')
        return redirect('home')

    context = {
        'post': post,
        'title': 'Удалить пост'
    }
    return render(request, 'posts/post_confirm_delete.html', context)


@login_required
def post_detail_view(request, pk):
    """Детальный просмотр поста + комментарии"""
    post = get_object_or_404(
        Post.objects.select_related('author', 'author__profile').prefetch_related('comments__author'),
        pk=pk,
    )

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен.')
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()

    context = {
        'post': post,
        'form': form,
        'comments': post.comments.all(),
        'title': f'Пост от {post.author.username}',
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_like_toggle_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    liked = False

    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'total_likes': post.likes.count()
        })

    next_url = request.POST.get('next') or request.GET.get('next') or 'home'
    if next_url == 'post_detail':
        return redirect('post_detail', pk=post.pk)
    return redirect(next_url)

@login_required
def post_comment_create_view(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен.')

    next_url = request.POST.get('next') or 'home'
    if next_url == 'post_detail':
        return redirect('post_detail', pk=post.pk)
    return redirect(next_url)