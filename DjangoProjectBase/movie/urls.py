from django.urls import path
from . import views

# Define un espacio de nombres para la app, es una buena práctica.
app_name = 'movie'

urlpatterns = [
    # Asigna la vista 'home' a la raíz de la app
    path('', views.home, name='home'),
    # La página de recomendación que estamos construyendo
    path('recommend/', views.recommend_movie, name='recommend_movie'),
    # Rutas para las otras vistas que tienes en views.py
    path('about/', views.about, name='about'),
    path('signup/', views.signup, name='signup'),
    path('statistics/', views.statistics_view, name='statistics'),
]