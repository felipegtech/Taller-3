import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Assign existing images from media/movie/images/ folder to movies in database"

    def handle(self, *args, **kwargs):
        # ✅ Folder where images are stored
        images_folder = 'media/movie/images/'
        
        # ✅ Check if folder exists
        if not os.path.exists(images_folder):
            self.stderr.write(f"Images folder not found: {images_folder}")
            return

        # ✅ Get all image files from the folder
        image_files = []
        for filename in os.listdir(images_folder):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                image_files.append(filename)
        
        self.stdout.write(f"Found {len(image_files)} image files: {image_files}")

        # ✅ Fetch all movies
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in database")

        # ✅ Create a mapping strategy
        assigned_count = 0
        
        for i, movie in enumerate(movies):
            try:
                # Strategy 1: Look for image with movie title pattern (m_Title.png)
                movie_image = None
                movie_title_clean = movie.title.replace(' ', '_').replace(':', '').replace('?', '').replace('!', '')
                
                # Look for exact match with m_ prefix
                expected_filename = f"m_{movie.title}.png"
                if expected_filename in image_files:
                    movie_image = expected_filename
                else:
                    # Look for similar patterns
                    for img_file in image_files:
                        if img_file.startswith('m_') and movie.title.lower() in img_file.lower():
                            movie_image = img_file
                            break
                
                # Strategy 2: If no specific match, assign available images in order
                if not movie_image and i < len(image_files):
                    # Skip default images for specific assignments
                    available_images = [img for img in image_files if img not in ['default.JPG', 'Captura.JPG', 'Sin_título.png']]
                    if i < len(available_images):
                        movie_image = available_images[i]
                    else:
                        # Use default as fallback
                        movie_image = 'default.JPG'

                if movie_image:
                    # ✅ Update database with image path
                    image_relative_path = f'movie/images/{movie_image}'
                    movie.image = image_relative_path
                    movie.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"✅ Assigned '{movie_image}' to '{movie.title}'"))
                    assigned_count += 1
                else:
                    self.stdout.write(self.style.WARNING(f"⚠ No suitable image found for '{movie.title}'"))

            except Exception as e:
                self.stderr.write(f"❌ Failed to assign image for '{movie.title}': {e}")

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Process completed! {assigned_count} movies updated with images."))
        self.stdout.write("📸 You can now run the Django server and check the movie images in the interface.")