from django.shortcuts import render
from inertia import render


def index(request):
    return render(request, 'Staff/Index')

def create(request):
    return render(request, 'Staff/Create')

def update(request):
    return render(request, 'Staff/Update')

def delete(request):
    return render(request, 'Staff/Delete')

def embedtestyt(request):
    return render(request, 'Staff/EmbedTestYT')

