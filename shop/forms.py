# shop/forms.py
from django import forms
import re
from datetime import datetime, timedelta

class ReservationForm(forms.Form):
    first_name = forms.CharField(
        label='Nombre', max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
        })
    )
    last_name = forms.CharField(
        label='Apellido', max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
        })
    )
    plate = forms.CharField(
        label='Matrícula', max_length=10,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
            'placeholder': '1234ABC'    
        })
    )
    phone = forms.CharField(
        label='Teléfono', max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
            'placeholder': '+34 600 000 000'
        })
    )
    quantity = forms.IntegerField(
        label='Cantidad', min_value=1, initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-orange-500',
            'placeholder': '1'
        })
    )

    def clean_plate(self):
        plate = self.cleaned_data.get('plate')
        if not re.match(r'^\d{4}[A-Z]{3}$', plate):
            raise forms.ValidationError('La matrícula debe tener 4 números seguidos de 3 letras mayúsculas (ejemplo: 1234ABC).')
        return plate

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^\+\d{2} \d{9}$', phone):
            raise forms.ValidationError('El teléfono debe tener el formato +XX XXXXXXXXX (ejemplo: +34 600000000).')
        return phone

    def save_reservation(self):
        expiration_time = datetime.now() + timedelta(hours=2)
        return expiration_time