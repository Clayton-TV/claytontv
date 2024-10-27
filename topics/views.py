from inertia import render
from django.http import HttpResponse

def index(request):
    return render(request, 'Topics')

