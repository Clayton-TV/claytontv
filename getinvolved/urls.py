from django.urls import path

from . import views

app_name = 'getinvolved'

urlpatterns = [
    path('give',    views.give,    name='give'),    # /getinvolved/give
    path('updates', views.updates, name='updates'), # /getinvolved/updates
]
