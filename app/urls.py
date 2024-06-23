"""
URL configuration for claytontv project.

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
from django.urls import path, include

from .views import index

urlpatterns = [
    path('', index, name='home'),
    path('catalogue/', include('catalogue.urls'), name='catalogue'),
    path('livestreams/', include('livestreams.urls'), name='livestreams'),
    path('staff/', include('staff.urls'), name='staff'),
    path('about/', include('about.urls'), name='about'),
    path('getinvolved/', include('getinvolved.urls'), name='getinvolved'),
    path('admin/', admin.site.urls),
]
