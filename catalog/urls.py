from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('videos/', views.VideoListView.as_view(), name='videos'),
    path('series/', views.SeriesListView.as_view(), name='series'),
    path('video/<int:pk>', views.VideoDetailView.as_view(), name='video-detail'),
    path('series/<int:pk>', views.SeriesDetailView.as_view(), name='series-detail'),
]