from django.urls import path

from . import views

app_name = 'catalogue'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.quick_results, name='quickbar_search_results'),
    path('<int:video_id>/', views.show, name='show'),
    path('about',     views.about,     name='about'),     # /about
    path('contact',   views.contact,   name='contact'),   # /contact
    path('donate',    views.donate,    name='donate'),    # /donate
    path('subscribe', views.subscribe, name='subscribe'), # /subscribe
    path('getinvolved/give',    views.give,    name='give'),    # /getinvolved/give
    path('getinvolved/updates', views.updates, name='updates'), # /getinvolved/updates
]
 