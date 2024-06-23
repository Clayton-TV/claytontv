from django.shortcuts import render
from inertia import render

def index(request):
    return render(request, 'About/Index')

def contact(request):
    return render(request, 'About/Contact')
