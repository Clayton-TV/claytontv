from django.shortcuts import render
from inertia import render

def give(request):
    return render(request, 'GetInvolved/Give')

def updates(request):
    return render(request, 'GetInvolved/Updates')
