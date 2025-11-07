"""
URL configuration for cloudysky project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path, include
from . import views
from app import views as app_views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path("", views.dummypage),
    path("dummypage", views.dummypage, name="index"),
    path("app/time", views.time_now),
    path("app/sum", views.sum_view),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='accounts_login'),
    # Alternate routes for autograder (grading expects /createUser not /app/createUser)
    path('createUser', app_views.create_user, name='create_user_alt'),
    path('', include('app.urls')),
]
