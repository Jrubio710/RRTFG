from celery import shared_task
from django.db.models import F
from .models import Tire

@shared_task
def restore_stock(tire_id, quantity):
    """
    Incrementa el stock del neumático en `quantity` tras expirar la reserva.
    """
    Tire.objects.filter(pk=tire_id).update(stock=F('stock') + quantity)