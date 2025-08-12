
from django.shortcuts import render
from restaurant.models import MenuItem

def home(request):
    recent_items = MenuItem.objects.all().order_by('-id')[:10]  # latest 10 items
    return render(request, 'home.html', {'recent_items': recent_items})
