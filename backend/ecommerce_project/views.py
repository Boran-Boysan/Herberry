from django.shortcuts import render

def landing_page(request):
    """Landing page view"""
    return render(request, 'landing.html')