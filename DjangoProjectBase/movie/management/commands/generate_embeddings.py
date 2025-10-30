import os
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv

from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = 'Genera y guarda los embeddings para las películas en la base de datos'

    def handle(self, *args, **kwargs):
        # Cargar la API Key de OpenAI
        try:
            load_dotenv('openAI.env')
            api_key = os.environ.get('openai_apikey')
            if not api_key:
                raise ValueError("La variable de entorno 'openai_apikey' no está definida en openAI.env")
            client = OpenAI(api_key=api_key)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al cargar la API key de OpenAI: {e}"))
            return

        self.stdout.write("Iniciando la generación de embeddings para las películas...")

        # Obtener todas las películas que aún no tienen un embedding
        movies_to_process = Movie.objects.filter(emb__isnull=True)
        
        if not movies_to_process.exists():
            self.stdout.write(self.style.SUCCESS("No hay películas nuevas para procesar. Todas ya tienen su embedding."))
            return

        for movie in movies_to_process:
            self.stdout.write(f"Procesando: '{movie.title}'...")
            # Combinar título y descripción para un embedding más rico
            text_to_embed = f"{movie.title}: {movie.description}"
            
            response = client.embeddings.create(input=[text_to_embed], model="text-embedding-3-small")
            embedding = np.array(response.data[0].embedding, dtype=np.float32)
            movie.emb = embedding.tobytes()
            movie.save()

        self.stdout.write(self.style.SUCCESS(f"¡Proceso completado! Se generaron embeddings para {movies_to_process.count()} películas."))