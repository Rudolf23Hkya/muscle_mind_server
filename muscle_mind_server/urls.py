"""
URL configuration for muscle_mind_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from testing import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('regUser/', views.register_new_user),
    path('loginUser/', views.login_user),
    path('loginUser_google/', views.login_with_google),
    path('user_with_access_token/', views.user_data_with_access_token),
    path('access_token_with_refresh_token/', views.access_token_with_refresh_token),
    path('workout_done/', views.workout_done),
    path('get_calories/', views.get_calories),
    path('add_calories/', views.add_eaten_calories),
    path('add_burnt_calories/', views.add_burnt_calories),
    path('get_stats/', views.get_stats)
]
