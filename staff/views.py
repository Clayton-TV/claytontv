from django.shortcuts import render
import django
from inertia import render


def index(request):
    django_version = django.get_version()

    return render(request, 'Staff.Videos', {
        'djangoVersion': django_version,
    })

def create(request):
    return render(request, 'Staff/Create')

def update(request):
    return render(request, 'Staff/Update')

def delete(request):
    return render(request, 'Staff/Delete')

