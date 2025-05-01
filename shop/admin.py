from django.contrib import admin
from django import forms
from .models import Employer, Tire, Client, Sale, Details

print("Archivo admin.py cargado correctamente")

admin.site.site_header = "Rubio Road - Panel de Administración"



# ------------------ Cliente ------------------
class ClientAdmin(admin.ModelAdmin):
    search_fields = ['name', 'plate', 'phone'] 
    list_display = ('name', 'plate', 'phone')   

admin.site.register(Client, ClientAdmin)

# ------------------ Detalles ------------------
class DetailsAdmin(admin.ModelAdmin):
    autocomplete_fields = ['sale', 'tire']  
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
    class Meta:
        model = Sale
        fields = '__all__'

# ------------------ Inline para detalles de la venta ------------------
class DetailsInline(admin.TabularInline):
    model = Details
    extra = 1
    fields = ('tire', 'quantity')
    autocomplete_fields = ['tire']  


# ------------------ Ventas ------------------
class SaleAdmin(admin.ModelAdmin):
    form = SaleForm
    autocomplete_fields = ['client', 'employer']  
    list_display = ('id', 'client', 'employer', 'date', 'total')
    inlines = [DetailsInline]
    search_fields = ['client__name', 'client__plate', 'id']  
    fieldsets = (
        ("Client Information", {
            'fields': ('client',)
        }),
        ("Sale Information", {
            'fields': ('employer',)
        }),
    )

admin.site.register(Sale, SaleAdmin)
