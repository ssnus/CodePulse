from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.SearchView.as_view(), name='search'),

    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),

    path('post/<int:pk>/like/', views.post_like_toggle, name='post_like_toggle'),
    path('post/<int:pk>/comment/', views.post_comment_create, name='post_comment_create'),
]