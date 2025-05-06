import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rubioroad.settings')

app = Celery('rubioroad')
# lee la configuración de CELERY_* en settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')
# Autodiscover tareas en apps instaladas
app.autodiscover_tasks()