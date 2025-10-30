# En el urls.py de tu PROYECTO
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Incluye las URLs de la app 'movie' para que sean accesibles desde la raíz del sitio
    path('', include('movie.urls')),
]