from django.shortcuts import get_object_or_404, render
from django.http import FileResponse
from django.db.models import F
import io
from reportlab.pdfgen import canvas
from django.utils import timezone

from .models import Tire
from .forms import ReservationForm
from .task import restore_stock

# Create your views here.
def home(request):
    featured_tires = Tire.objects.all()[:3]
    return render(request, 'home.html', {
        'featured_tires': featured_tires
    })

def tire_list(request):
    tires = Tire.objects.filter(stock__gt=0)  # Solo mostrar ruedas con stock
    return render(request, 'tire_list.html', {'tires': tires})

def reserve_tire(request, tire_id):
    tire = get_object_or_404(Tire, pk=tire_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity']
            # 1) Comprobar stock suficiente y descontar atómicamente
            updated = Tire.objects.filter(pk=tire.id, stock__gte=qty)\
                                  .update(stock=F('stock') - qty)
            if not updated:
                form.add_error('quantity', 'No hay suficiente stock para esa cantidad.')
            else:
                # 2) Programar restauración en 2 horas
                restore_stock.apply_async(args=[tire.id, qty], countdown=7200)

                # 3) Generar PDF
                buffer = io.BytesIO()
                p = canvas.Canvas(buffer)
                p.setFont("Helvetica-Bold", 14)
                p.drawString(50, 800, "Comprobante de Reserva RubioRoad")
                p.setFont("Helvetica", 12)
                p.drawString(50, 770,
                    f"Neumático: {tire.brand} {tire.model} ({tire.dimensions}) x {qty}")
                p.drawString(50, 750,
                    f"Cliente: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']}")
                p.drawString(50, 730, f"Matrícula: {form.cleaned_data['plate']}")
                p.drawString(50, 710, f"Teléfono: {form.cleaned_data['phone']}")
                p.drawString(50, 690,
                    f"Fecha y hora: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
                p.drawString(50, 660, "– Reserva válida por 2 horas –")
                p.showPage()
                p.save()
                buffer.seek(0)
                return FileResponse(
                    buffer,
                    as_attachment=True,
                    filename='reserva_rubioroad.pdf'
                )
    else:
        form = ReservationForm()

    return render(request, 'reserve.html', {
        'form': form,
        'tire': tire
    })