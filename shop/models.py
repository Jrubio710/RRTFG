from django.db import models

class Employer(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.email})"

class Tire(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    dimensions = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.IntegerField()

    def __str__(self):
        return f"{self.brand} {self.model} ({self.dimensions})"

class Client(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    plate = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"Name: {self.name} {self.plate}"
    
class Sale(models.Model):
    id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, related_name='sales', on_delete=models.CASCADE)
    employer = models.ForeignKey(Employer, related_name='sales', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return f"Sale {self.id} - {self.client.name} ({self.date.strftime('%H:%M:%S')}) ({self.total})"
    def update_total(self):
        """Actualiza el total de la venta sumando los subtotales de los detalles."""
        total = sum(detail.subtotal for detail in self.details.all())
        self.total = total
        self.save()

class Details(models.Model):
    id = models.AutoField(primary_key=True)
    sale = models.ForeignKey(Sale, related_name='details', on_delete=models.CASCADE)
    tire = models.ForeignKey(Tire, related_name='details', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        """Calcula el subtotal y actualiza el stock del neumático cuando se guarda el detalle."""
        self.subtotal = self.tire.price * self.quantity
        self.tire.stock -= self.quantity
        self.tire.save()  
        super().save(*args, **kwargs)
        
        # Luego actualizamos el total de la venta
        self.sale.update_total()