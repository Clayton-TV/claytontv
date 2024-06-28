from django.urls import path

from . import views

app_name = 'static'

urlpatterns = [
    path('about',     views.about,     name='about'),     # /about
    path('contact',   views.contact,   name='contact'),   # /contact
    path('donate',    views.donate,    name='donate'),    # /donate
    path('subscribe', views.subscribe, name='subscribe'), # /subscribe
]
