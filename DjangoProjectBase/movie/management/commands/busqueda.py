from openai import OpenAI
import numpy as np
import os
from dotenv import load_dotenv
from movie.models import Movie

# Cargar la API Key
load_dotenv('openAI.env')
client = OpenAI(api_key=os.environ.get('openai_apikey'))

# Función para calcular similitud de coseno
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Recibir el prompt del usuario (esto se debe recibir desde el formulario de la app)
prompt = "película de la segunda guerra mundial"

# Generar embedding del prompt
response = client.embeddings.create(
    input=[prompt],
    model="text-embedding-3-small"
)
prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)

# Recorrer la base de datos y comparar
best_movie = None
max_similarity = -1

for movie in Movie.objects.all():
    movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
    similarity = cosine_similarity(prompt_emb, movie_emb)

    if similarity > max_similarity:
        max_similarity = similarity
        best_movie = movie

print(f"La película más similar al prompt es: {best_movie.title} con similitud {max_similarity:.4f}")