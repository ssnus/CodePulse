from django.urls import path
from . import views

urlpatterns = [
    path('edit/', views.profile_edit_view, name='profile_edit'),
    path('<str:username>/', views.profile_view, name='profile'),
    path('<str:username>/follow/', views.follow_toggle_view, name='follow_toggle'),
]