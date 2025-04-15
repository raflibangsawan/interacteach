import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interacteach.settings')
django.setup()

from django.contrib.auth.models import User

def create_superuser():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin')
    
    if not password:
        print("Error: DJANGO_SUPERUSER_PASSWORD environment variable not set")
        return
    
    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists")
        return
    
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully")

if __name__ == "__main__":
    create_superuser()
