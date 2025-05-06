import io
import os
from datetime import timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.http import FileResponse
from django.db.models import F
from django.utils import timezone
from django.contrib import messages

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from .models import Tire
from .forms import ReservationForm
from .task import restore_stock

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
            updated = Tire.objects.filter(pk=tire.id, stock__gte=qty).update(stock=F('stock') - qty)
            if not updated:
                form.add_error('quantity', 'No hay suficiente stock para esa cantidad.')
            else:
                restore_stock.apply_async(args=[tire.id, qty], countdown=7200)

                # Generar PDF
                buffer = io.BytesIO()
                p = canvas.Canvas(buffer, pagesize=A4)
                width, height = A4

                p.setFillColor(colors.HexColor('#FF6600'))
                p.rect(0, height - 40*mm, width, 40*mm, fill=True, stroke=False)
                p.setFont("Helvetica-Bold", 18)
                p.setFillColor(colors.white)
                p.drawCentredString(width/2, height - 25*mm, "COMPROBANTE DE RESERVA")

                p.setStrokeColor(colors.black)
                p.setLineWidth(1)
                p.line(15*mm, height - 45*mm, width - 15*mm, height - 45*mm)

                p.setFillColor(colors.white)
                p.roundRect(15*mm, height - 150*mm, width - 30*mm, 100*mm, 5*mm, fill=True, stroke=False)

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

                p.setFillColor(colors.black)
                p.setFont("Helvetica", 10)
                p.drawString(x, y - 7*line, "--------------------------------------------------------------------")

                p.setFont("Helvetica-Bold", 12)
                p.setFillColor(colors.HexColor('#FF6600'))
                p.drawString(x, y - 9*line, "Contacto de RubioRoad")
                p.setFont("Helvetica", 10)
                p.setFillColor(colors.black)
                p.drawString(x, y - 10*line, "Teléfono: +34 912 345 678")
                p.drawString(x, y - 11*line, "Dirección: Calle Martin Ruiz 12, 41900 Sevilla")
                p.drawString(x, y - 12*line, "Email: contacto@rubioroad.com")

                p.setFont("Helvetica-Oblique", 10)
                p.setFillColor(colors.gray)
                p.drawCentredString(width/2, 15*mm, "Gracias por confiar en RubioRoad. ¡Te esperamos!")
                p.drawCentredString(width / 2, 10 * mm, "Puedes cerrar esta pestaña tras guardar el archivo.")
                p.drawCentredString(width / 2, 6 * mm, "Visítanos de nuevo en www.rubioroad.com")

                p.showPage()
                p.save()
                buffer.seek(0)

                # Guardar el PDF en media/pdfs/
                pdf_filename = f"reserva_{now.strftime('%Y%m%d%H%M%S')}.pdf"
                pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', pdf_filename)
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                with open(pdf_path, 'wb') as f:
                    f.write(buffer.read())

                # Guardar URL en sesión
                request.session['pdf_url'] = os.path.join(settings.MEDIA_URL, 'pdfs', pdf_filename)

                messages.success(request, "Reserva realizada correctamente.")
                return redirect('reservation_success')

    else:
        form = ReservationForm()

    return render(request, 'reserve.html', {
        'form': form,
        'tire': tire
    })

def reservation_success(request):
    pdf_url = request.session.pop('pdf_url', None)
    return render(request, 'reservation_success.html', {
        'pdf_url': pdf_url
    })
