from django.contrib import admin
from django import forms
from .models import Employer, Tire, Client, Sale, Details

print("Archivo admin.py cargado correctamente")

# ------------------ Cliente ------------------
class ClientAdmin(admin.ModelAdmin):
    search_fields = ['name', 'plate', 'phone']  # Autocompletado por nombre, matrícula o teléfono
    list_display = ('name', 'plate', 'phone')   # Muestra el teléfono también

admin.site.register(Client, ClientAdmin)

# ------------------ Detalles ------------------
class DetailsAdmin(admin.ModelAdmin):
    autocomplete_fields = ['sale', 'tire']  # 🔁 Activa el autocompletado en relaciones ForeignKey
    search_fields = ['sale__client__name', 'tire__model']
    list_display = ('sale', 'tire', 'quantity')

admin.site.register(Details, DetailsAdmin)

# ------------------ Neumáticos ------------------
class TireAdmin(admin.ModelAdmin):
    search_fields = ['brand', 'model', 'dimensions']
    list_display = ('brand', 'model', 'dimensions', 'price', 'stock')

admin.site.register(Tire, TireAdmin)

# ------------------ Empleados ------------------
class EmployerAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email']
    list_display = ('name', 'email')

admin.site.register(Employer, EmployerAdmin)

# ------------------ Formulario personalizado para Ventas ------------------
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

# ------------------ Inline para detalles de la venta ------------------
class DetailsInline(admin.TabularInline):
    model = Details
    extra = 1
    fields = ('tire', 'quantity')
    autocomplete_fields = ['tire']  # 🔁 Esto activa el buscador para los neumáticos


# ------------------ Ventas ------------------
class SaleAdmin(admin.ModelAdmin):
    form = SaleForm
    autocomplete_fields = ['client', 'employer']  # 🔁 Autocompletado para cliente y empleado
    list_display = ('id', 'client', 'employer', 'date', 'total')
    inlines = [DetailsInline]
    search_fields = ['client__name', 'client__plate', 'id']  # Necesario por autocomplete en DetailsAdmin
    fieldsets = (
        ("Client Information", {
            'fields': ('client', 'new_client_name', 'new_client_phone', 'new_client_plate')
        }),
        ("Sale Information", {
            'fields': ('employer',)
        }),
    )

admin.site.register(Sale, SaleAdmin)
