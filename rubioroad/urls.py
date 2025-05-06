from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from shop import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',       views.home,             name='home'),
    path('tires/', views.tire_list,        name='tire_list'),
    path('reserve/<int:tire_id>/', views.reserve_tire, name='reserve_tire'),
    path('success/', views.reservation_success, name='reservation_success'),  # Asegúrate de tener esta línea también
]

# Añadir soporte para archivos media (como los PDF generados)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
