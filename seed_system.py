import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'public.settings')
django.setup()

from myapp.models import District, EmergencyType

# Add Districts
districts = ["Thiruvananthapuram", "Kochi", "Kozhikode", "Wayanad", "Idukki"]
for d in districts:
    District.objects.get_or_create(name=d, state="Kerala")

# Add Emergency Types
emergency_types = [
    ("Flood", "Inundation of land by water"),
    ("Landslide", "Movement of rock, debris, or earth down a slope"),
    ("Fire", "Outbreak of fire in buildings or forests"),
    ("Cyclone", "Strong winds and heavy rain"),
    ("Medical Emergency", "Urgent health crisis requiring rescue")
]

for name, desc in emergency_types:
    EmergencyType.objects.get_or_create(name=name, description=desc)

print("Seed data for Districts and Emergency Types added successfully.")
