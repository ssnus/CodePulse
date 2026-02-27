from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),

    path('<str:username>/', views.ProfileDetailView.as_view(), name='profile'),

    path('<str:username>/follow/', views.FollowToggleView.as_view(), name='follow_toggle'),
]