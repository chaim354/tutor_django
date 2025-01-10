from django.urls import path, include
from .import views

app_name = 'users'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('register/', views.register, name='register'),
    path('google_calendar_redirect/', views.google_calendar_redirect, name='google_calendar_redirect'),
]