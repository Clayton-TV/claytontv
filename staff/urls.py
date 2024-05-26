from django.urls import path

from . import views

app_name = 'staff'

urlpatterns = [
    path('videos',        views.index,  name='index'),  # /staff/videos
    path('videos/create', views.create, name='create'), # /staff/videos/create
    #path('<int:video_id>/', views.show, name='show'),
]
