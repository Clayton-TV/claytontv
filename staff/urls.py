from django.urls import path

from . import views

app_name = 'staff'

urlpatterns = [
    path('videos',        views.index,  name='index'),  # /staff/videos
    path('videos/create', views.create, name='create'), # /staff/videos/create
    path('videos/update', views.update, name='update'), # /staff/videos/update
    path('videos/delete', views.delete, name='delete'), # /staff/videos/delete
    path('videos/embedtest-yt', views.embedtestyt, name='embedtestyt'), # /staff/videos/embedtestyt
    #path('<int:video_id>/', views.show, name='show'),
]
