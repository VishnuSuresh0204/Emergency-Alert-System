from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime

class Login(AbstractUser):
    userType = models.CharField(max_length=50)  
    # admin / staff / volunteer / user
    viewPass = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username

class District(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=100, default="Kerala")

    def __str__(self):
        return self.name

class Citizen(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=300)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    profile_pic = models.ImageField(upload_to="citizen_profile", null=True, blank=True)
    status = models.CharField(max_length=40, default="active")

    def __str__(self):
        return self.name

class Staff(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.CharField(max_length=200)
    profile_pic = models.ImageField(upload_to="staff_profile", null=True, blank=True)
    status = models.CharField(max_length=40, default="active")

    def __str__(self):
        return self.name

class Volunteer(models.Model):
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.TextField(default="", help_text="e.g., First Aid, Swimming, Driving")
    availability_status = models.CharField(max_length=50, default="Available")
    profile_pic = models.ImageField(upload_to="volunteer_profile", null=True, blank=True)
    status = models.CharField(max_length=40, default="Pending") # Admin approval needed

    def __str__(self):
        return self.name

class EmergencyType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.ImageField(upload_to="emergency_icons", null=True, blank=True)

    def __str__(self):
        return self.name

class EmergencyReport(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending Verification'),
        ('Verified', 'Verified'),
        ('Active', 'Rescue Operations Ongoing'),
        ('Resolved', 'Situation Resolved'),
        ('Fake', 'Fake Report'),
    ]
    user = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    emergency_type = models.ForeignKey(EmergencyType, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    location_details = models.TextField()
    description = models.TextField()
    image = models.ImageField(upload_to="emergency_reports", null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    latitude = models.CharField(max_length=50, null=True, blank=True)
    longitude = models.CharField(max_length=50, null=True, blank=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    verified_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(default="")

    def __str__(self):
        return f"{self.emergency_type.name} at {self.location_details[:30]}"

class RescueRequest(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High (Life Threatening)'),
        ('Medium', 'Medium (Injured/Trapped)'),
        ('Low', 'Low (Stranded/Needs Supplies)'),
    ]
    report = models.ForeignKey(EmergencyReport, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    contact_person = models.CharField(max_length=200)
    contact_phone = models.CharField(max_length=20)
    number_of_people = models.IntegerField(default=1)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    message = models.TextField()
    status = models.CharField(max_length=50, default="Pending") # Pending, Assigned, Rescued
    assigned_volunteers = models.ManyToManyField(Volunteer, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rescue for {self.contact_person} - {self.priority}"

class EmergencyAlert(models.Model):
    LEVEL_CHOICES = [
        ('Red', 'Red Alert (Extreme Danger)'),
        ('Orange', 'Orange Alert (High Risk)'),
        ('Yellow', 'Yellow Alert (Precaution)'),
        ('Green', 'Green (Safe/Update)'),
    ]
    title = models.CharField(max_length=300)
    message = models.TextField()
    alert_level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    posted_by = models.ForeignKey(Login, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Feedback(models.Model):
    user = models.ForeignKey(Citizen, on_delete=models.CASCADE, null=True, blank=True)
    subject = models.CharField(max_length=200, default="General")
    message = models.TextField()
    admin_reply = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.name}"

class Notification(models.Model):
    user = models.ForeignKey(Login, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"

class UrgentWorkRequest(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class UrgentWorkResponse(models.Model):
    request = models.ForeignKey(UrgentWorkRequest, on_delete=models.CASCADE)
    volunteer = models.ForeignKey(Volunteer, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default="Pending") # Pending, Accepted
    created_at = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    sender = models.ForeignKey(Login, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(Login, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
