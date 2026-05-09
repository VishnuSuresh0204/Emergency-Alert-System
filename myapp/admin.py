from django.contrib import admin
from .models import *

admin.site.register(Login)
admin.site.register(District)
admin.site.register(Citizen)
admin.site.register(Staff)
admin.site.register(Volunteer)
admin.site.register(EmergencyType)
admin.site.register(EmergencyReport)
admin.site.register(RescueRequest)
admin.site.register(EmergencyAlert)
admin.site.register(Feedback)