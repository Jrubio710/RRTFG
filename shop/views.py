from datetime import timedelta
from django.shortcuts import get_object_or_404, render
from django.http import FileResponse
from django.db.models import F
from django.utils import timezone
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas

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
    tires = Tire.objects.filter(stock__gt=0)  
    return render(request, 'tire_list.html', {'tires': tires})

def reserve_tire(request, tire_id):
    tire = get_object_or_404(Tire, pk=tire_id)
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            qty = form.cleaned_data['quantity']
            
            updated = Tire.objects.filter(pk=tire.id, stock__gte=qty)\
                                  .update(stock=F('stock') - qty)
            if not updated:
                form.add_error('quantity', 'No hay suficiente stock para esa cantidad.')
            else:
                
                restore_stock.apply_async(args=[tire.id, qty], countdown=7200)

               
                buffer = io.BytesIO()
                p = canvas.Canvas(buffer, pagesize=A4)
                width, height = A4

                # — Header con fondo naranja y texto blanco —
                p.setFillColor(colors.HexColor('#FF6600'))
                p.rect(0, height - 40*mm, width, 40*mm, fill=True, stroke=False)
                p.setFont("Helvetica-Bold", 18)
                p.setFillColor(colors.white)
                p.drawCentredString(width/2, height - 25*mm, "COMPROBANTE DE RESERVA")

                # — Línea separadora —
                p.setStrokeColor(colors.black)
                p.setLineWidth(1)
                p.line(15*mm, height - 45*mm, width - 15*mm, height - 45*mm)

                # — Cuerpo blanco semitransparente —
                p.setFillColor(colors.white)
                p.roundRect(15*mm, height - 150*mm, width - 30*mm, 100*mm, 5*mm, fill=True, stroke=False)

                # — Datos del cliente y reserva —
                x = 20*mm
                y = height - 50*mm
                line = 7*mm
                p.setFont("Helvetica", 12)
                p.setFillColor(colors.black)
                p.drawString(x, y, f"Neumático: {tire.brand} {tire.model} ({tire.dimensions}) x{qty}")
                p.drawString(x, y - line, f"Cliente: {form.cleaned_data['first_name']} {form.cleaned_data['last_name']}")
                p.drawString(x, y - 2*line, f"Matrícula: {form.cleaned_data['plate']}")
                p.drawString(x, y - 3*line, f"Teléfono: {form.cleaned_data['phone']}")
                now = timezone.now()
                p.drawString(x, y - 4*line, f"Fecha reserva: {now.strftime('%Y-%m-%d %H:%M')}")
                expire = now + timedelta(hours=2)
                p.setFillColor(colors.HexColor('#CC3300'))
                p.drawString(x, y - 5*line, f"Válida hasta: {expire.strftime('%Y-%m-%d %H:%M')}")

                # — Espaciado y separadores para una mejor lectura —
                p.setFillColor(colors.black)
                p.setFont("Helvetica", 10)
                p.drawString(x, y - 7*line, "--------------------------------------------------------------------")

                # — Información de la empresa —
                p.setFont("Helvetica-Bold", 12)
                p.setFillColor(colors.HexColor('#FF6600'))
                p.drawString(x, y - 9*line, "Contacto de RubioRoad")
                p.setFont("Helvetica", 10)
                p.setFillColor(colors.black)
                p.drawString(x, y - 10*line, "Teléfono: +34 912 345 678")
                p.drawString(x, y - 11*line, "Dirección: Calle Martin Ruiz 12, 41900 Sevilla")
                p.drawString(x, y - 12*line, "Email: contacto@rubioroad.com")

                # — Footer —
                p.setFont("Helvetica-Oblique", 10)
                p.setFillColor(colors.gray)
                p.drawCentredString(width/2, 15*mm, "Gracias por confiar en RubioRoad. ¡Te esperamos!")

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