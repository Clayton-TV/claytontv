from django.shortcuts import render
from inertia import render


def about(request):
    return render(request, 'Static Pages/About')

def contact(request):
    return render(request, 'Static Pages/Contact Information')

def donate(request):
    return render(request, 'Static Pages/Donation')

def subscribe(request):
    return render(request, 'Static Pages/Subscribe')
