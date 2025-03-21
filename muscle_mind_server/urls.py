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
from testing import views_auth
from testing import views

urlpatterns = [
    #NOT PART OF THE REST API
    path('admin/', admin.site.urls),
    
    # authentication
    path('regUser/', views_auth.register_new_user),
    path('loginUser/', views_auth.login_user),
    path('handle_oAuth_google_token/', views_auth.handle_oAuth_google_token),
    path('access_token/', views_auth.get_access_token),
    # data layer
    path('get_calories/', views.get_calories),
    path('add_calories/', views.add_calories),
    
    path('get_recom_workouts/', views.get_recom_workouts),
    path('post_user_workout/', views.post_user_workout),
    path('get_user_workout/', views.get_user_workout),
    path('workout_done/', views.workout_done),
    
    # stats
    path('get_stats/', views.get_stats),
    path('get_stats_via_email/', views.get_stats_via_email)
]
