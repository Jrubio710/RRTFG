from django.shortcuts import render
from .models import Tire

# Create your views here.
def home(request):
    featured_tires = Tire.objects.all()[:3]
    return render(request, 'home.html', {
        'featured_tires': featured_tires
    })

def tire_list(request):
    tires = Tire.objects.filter(stock__gt=0)  # Solo mostrar ruedas con stock
    return render(request, 'tire_list.html', {'tires': tires})