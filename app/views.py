import django
from inertia import render


def index(request):
    django_version = django.get_version()

    return render(request, 'Welcome', {
        'djangoVersion': django_version,
    })
