from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('donate/', views.donate, name='donate'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('help/', views.helppage, name='help'),
    path('contact/', views.contact, name='contact'),
    path('privacy/',views.privacy, name='privacy'),
    path('videos/', views.VideoListView.as_view(), name='videos'),
    path('series/', views.SeriesListView.as_view(), name='series'),
    path('video/<int:pk>', views.VideoDetailView.as_view(), name='video-detail'),
    path('series/<int:pk>', views.SeriesDetailView.as_view(), name='series-detail'),
]