# shop/forms.py
from django import forms

class ReservationForm(forms.Form):
    first_name = forms.CharField(label='Nombre', max_length=100)
    last_name  = forms.CharField(label='Apellido', max_length=100)
    plate      = forms.CharField(label='Matrícula', max_length=10)
    phone      = forms.CharField(label='Teléfono', max_length=15)
    quantity   = forms.IntegerField(
        label='Cantidad de neumáticos',
        min_value=1,
        initial=1
    )
