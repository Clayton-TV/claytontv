from django.urls import path

from . import views

app_name = 'catalogue'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:video_id>/', views.show, name='show'),
]
