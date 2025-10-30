from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie

import matplotlib
import io
import urllib, base64
import matplotlib.pyplot as plt

# Imports para la vista de recomendación
from openai import OpenAI
import numpy as np
import os
from dotenv import load_dotenv
from django.conf import settings

# Carga las variables de entorno desde el archivo openAI.env que está en la raíz del proyecto
load_dotenv(os.path.join(settings.BASE_DIR, 'openAI.env'))
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))


def cosine_similarity(a, b):
    """Calcula la similitud de coseno entre dos vectores."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def home(request):
    #return HttpResponse('<h1>Welcome to Home Page</h1>')
    searchTerm = request.GET.get('searchMovie') 
    if searchTerm: 
        movies = Movie.objects.filter(title__icontains=searchTerm) 
    else: 
        movies = Movie.objects.all() 
    return render(request, 'movie/home.html', {'searchTerm':searchTerm, 'movies': movies})

def about(request):
    return HttpResponse('<h1>Welcome to About Page</h1>')

def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email':email})

def statistics_view(request):
    matplotlib.use('Agg')

    all_movies = Movie.objects.all()
    movie_counts_by_year = {}

    for movie in all_movies:
        year = movie.year if movie.year else "None"
        if year in movie_counts_by_year:
            movie_counts_by_year[year] += 1
        else:
            movie_counts_by_year[year] = 1

    bar_width = 0.5
    bar_positions = np.arange(len(movie_counts_by_year))

    plt.figure(figsize=(10, 6))
    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')

    plt.title('Movie counts by year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)

    plt.subplots_adjust(bottom=0.3)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'statistics.html', {'graphic': graphic})

def recommend_movie(request):
    """
    Vista para recomendar una película basada en un prompt de texto.
    """
    context = {}
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '')
        context['prompt'] = prompt

        if prompt:
            try:
                # 1. Generar el embedding del prompt usando la API de OpenAI
                response = client.embeddings.create(
                    input=[prompt],
                    model="text-embedding-3-small"
                )
                prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)

                # 2. Recorrer la base de datos y calcular la similitud
                best_movie = None
                max_similarity = -1

                for movie in Movie.objects.all():
                    if movie.emb: # Asegurarse que la película tiene un embedding
                        movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                        similarity = cosine_similarity(prompt_emb, movie_emb)

                        if similarity > max_similarity:
                            max_similarity = similarity
                            best_movie = movie
                context['best_movie'] = best_movie
                context['similarity'] = max_similarity
            except Exception as e:
                context['error'] = f"Ocurrió un error al procesar tu solicitud: {e}"
    return render(request, 'movie/recommend.html', context)
