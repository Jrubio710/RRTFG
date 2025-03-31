import os
import django
import random
from faker import Faker

# Configurar Django antes de importar modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rubioroad.settings')  # Cambia si tu proyecto tiene otro nombre
django.setup()

# Importar modelos
from shop.models import Employer, Tire, Client, Sale, Details  # Asegúrate de que 'shop' es el nombre correcto de tu app

# Instancia Faker
fake = Faker('es_ES')  # Datos en español

def create_employers(n=10):
    """Crea 'n' empleados ficticios respetando los max_length."""
    for _ in range(n):
        Employer.objects.create(
            name=fake.name()[:100],  # Máximo 100 caracteres
            email=fake.unique.email()[:254],  # Django EmailField permite hasta 254
            password=fake.password(length=10)[:50]  # Máximo 50 caracteres
        )

def create_clients(n=20):
    """Crea 'n' clientes ficticios respetando los max_length."""
    for _ in range(n):
        Client.objects.create(
            name=fake.name()[:100],  # Máximo 100 caracteres
            phone=fake.phone_number()[:15],  # Máximo 15 caracteres
            plate=fake.unique.license_plate()[:10]  # Máximo 10 caracteres
        )

def create_tires(n=30):
    """Crea 'n' neumáticos ficticios respetando los max_length."""
    for _ in range(n):
        Tire.objects.create(
            brand=fake.company()[:100],  # Máximo 100 caracteres
            model=fake.word()[:100],  # Máximo 100 caracteres
            dimensions=f"{random.randint(165, 225)}/{random.randint(50, 70)} R{random.choice([14, 15, 16, 17, 18])}"[:50],  # Máximo 50 caracteres
            price=round(random.uniform(50, 500), 2),
            stock=random.randint(10, 100)
        )

def create_sales(n=15):
    """Crea 'n' ventas ficticias con detalles aleatorios respetando los max_length."""
    clients = list(Client.objects.all())
    employers = list(Employer.objects.all())
    tires = list(Tire.objects.all())

    if not clients or not employers or not tires:
        print("No hay suficientes registros para crear ventas")
        return

    for _ in range(n):
        sale = Sale.objects.create(
            client=random.choice(clients),
            employer=random.choice(employers),
            total=0  # Se calculará después
        )

        total = 0
        for _ in range(random.randint(1, 5)):  # Cada venta tiene entre 1 y 5 neumáticos
            tire = random.choice(tires)
            quantity = random.randint(1, 4)
            subtotal = round(tire.price * quantity, 2)

            Details.objects.create(
                sale=sale,
                tire=tire,
                quantity=quantity,
                subtotal=subtotal
            )

            total += subtotal

        # Actualizar total de la venta
        sale.total = round(total, 2)
        sale.save()

def populate_db():
    """Ejecuta la generación de datos ficticios."""
    create_employers(10)
    create_clients(20)
    create_tires(30)
    create_sales(15)
    print("Base de datos poblada con datos ficticios")

# Ejecutar la función principal
if __name__ == "__main__":
    populate_db()