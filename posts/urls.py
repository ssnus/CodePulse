from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('post/create/', views.post_create_view, name='post_create'),
    path('post/<int:pk>/delete/', views.post_delete_view, name='post_delete'),
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('post/<int:pk>/like/', views.post_like_toggle_view, name='post_like_toggle'),
    path('post/<int:pk>/comment/', views.post_comment_create_view, name='post_comment_create'),
]