import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public.settings')
django.setup()

from myapp.models import Login

if not Login.objects.filter(username='admin').exists():
    Login.objects.create_superuser('admin', 'admin@example.com', 'admin123', userType='admin')
    print("Superuser 'admin' created successfully with password 'admin123'")
else:
    print("Superuser 'admin' already exists")
