from django.contrib import admin
from django import forms
from django.utils.html import format_html
from .models import Employer, Tire, Client, Sale, Details

print("Archivo admin.py cargado correctamente")

# Configuración del admin para Cliente
class ClientAdmin(admin.ModelAdmin):
    search_fields = ['name', 'plate'] 
    list_display = ('name', 'plate')  

admin.site.register(Client, ClientAdmin) 

# Configuración del admin para Detalles
class DetailsAdmin(admin.ModelAdmin):
    search_fields = ['sale__client__name', 'tire__model'] 
    list_display = ('sale', 'tire', 'quantity') 



# Configuración del admin para Neumáticos
class TireAdmin(admin.ModelAdmin):
    search_fields = ['brand', 'model', 'dimensions']
    list_display = ('brand', 'model', 'dimensions', 'price', 'stock')

admin.site.register(Tire, TireAdmin)

# Configuración del admin para Empleados
class EmployerAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email']
    list_display = ('name', 'email')

admin.site.register(Employer, EmployerAdmin)

# FORMULARIO PERSONALIZADO PARA VENTAS
class SaleForm(forms.ModelForm):
    new_client_name = forms.CharField(required=False, label="New Client - Name")
    new_client_phone = forms.CharField(required=False, label="Phone")
    new_client_plate = forms.CharField(required=False, label="Plate")
    total = forms.DecimalField(required=False, label="Total", widget=forms.NumberInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = Sale
        fields = '__all__' 

    def clean(self):
        cleaned_data = super().clean()
        new_name = cleaned_data.get("new_client_name")
        new_phone = cleaned_data.get("new_client_phone")
        new_plate = cleaned_data.get("new_client_plate")

        if new_name and new_plate:
            if Client.objects.filter(plate=new_plate).exists():
                raise forms.ValidationError("Already exist a client with this plate.")

            # Crear cliente nuevo
            new_client = Client.objects.create(
                name=new_name,
                phone=new_phone,
                plate=new_plate
            )
            cleaned_data["client"] = new_client 
        
        return cleaned_data


class DetailsInline(admin.TabularInline):
    model = Details
    extra = 1 
    fields = ('tire', 'quantity') 

    # Restamos el stock y calculamos el subtotal al guardar el modelo
    def save_model(self, request, obj, form, change):
        # Calculamos el subtotal (precio * cantidad)
        obj.subtotal = obj.tire.price * obj.quantity
        obj.tire.stock -= obj.quantity  
        obj.tire.save() 
        super().save_model(request, obj, form, change)
        
        # Actualizar total en la venta
        obj.sale.update_total()

# Configuración del admin para Ventas
class SaleAdmin(admin.ModelAdmin):
    form = SaleForm
    list_display = ('id', 'client', 'employer', 'date', 'total')
    inlines = [DetailsInline]  # Agrega la opción de seleccionar neumáticos
    fieldsets = (
        ("Client Information", {
            'fields': ('client', 'new_client_name', 'new_client_phone', 'new_client_plate')
        }),
        ("Sale Information", {
            'fields': ('employer',)
        }),
    )


admin.site.register(Sale, SaleAdmin) 