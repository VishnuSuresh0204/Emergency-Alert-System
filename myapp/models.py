from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import datetime


class Login(AbstractUser):
    userType = models.CharField(max_length=50)  
    # admin / authority / customer
    viewPass = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.username


class Customer(models.Model):
    """Formerly Citizen - Represents customers applying for certificates"""
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=300)
    date_of_birth = models.DateField(null=True, blank=True)
    aadhar_number = models.CharField(max_length=12, null=True, blank=True)
    profile_pic = models.ImageField(upload_to="customer_profile", null=True, blank=True)
    status = models.CharField(max_length=40, default="active")

    def __str__(self):
        return self.name


class Authority(models.Model):
    """Government authorities who process certificate requests"""
    loginid = models.ForeignKey(Login, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    designation = models.CharField(max_length=200)
    office_address = models.CharField(max_length=300)
    profile_pic = models.ImageField(upload_to="authority_profile", null=True, blank=True)
    status = models.CharField(max_length=40, default="active")

    def __str__(self):
        return f"{self.name} - {self.designation}"

    class Meta:
        verbose_name_plural = "Authorities"


class CertificateType(models.Model):
    """Types of certificates available in the system"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()
    base_fee = models.DecimalField(max_digits=10, decimal_places=2)
    processing_days = models.IntegerField(help_text="Typical processing time in days")
    required_documents = models.TextField(help_text="List of required documents")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class CertificateRequest(models.Model):
    """Customer applications for certificates"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Forwarded', 'Forwarded to Authority'),
        ('Under Review', 'Under Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Issued', 'Certificate Issued'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    certificate_type = models.ForeignKey(CertificateType, on_delete=models.CASCADE)
    application_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Applicant details stored as text fields for flexibility
    applicant_name = models.CharField(max_length=200)
    applicant_father_name = models.CharField(max_length=200, blank=True, null=True)
    applicant_mother_name = models.CharField(max_length=200, blank=True, null=True)
    applicant_dob = models.DateField(blank=True, null=True)
    applicant_address = models.TextField()
    additional_details = models.TextField(blank=True, null=True, help_text="Additional details specific to certificate type")
    
    # Supporting documents
    document1 = models.FileField(upload_to="certificate_documents", null=True, blank=True)
    document2 = models.FileField(upload_to="certificate_documents", null=True, blank=True)
    document3 = models.FileField(upload_to="certificate_documents", null=True, blank=True)
    document4 = models.FileField(upload_to="certificate_documents", null=True, blank=True)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    assigned_authority = models.ForeignKey(Authority, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    
    applied_date = models.DateTimeField(auto_now_add=True)
    forwarded_date = models.DateTimeField(null=True, blank=True)
    processed_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.application_number:
            # Generate application number: CERT-YYYY-NNNN
            year = datetime.now().year
            count = CertificateRequest.objects.filter(
                application_number__startswith=f'CERT-{year}'
            ).count() + 1
            self.application_number = f'CERT-{year}-{count:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.application_number} - {self.certificate_type.name}"

    class Meta:
        ordering = ['-applied_date']


class Payment(models.Model):
    """Payment records for certificates"""
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Online', 'Online Payment'),
        ('Cash', 'Cash'),
        ('Card', 'Debit/Credit Card'),
        ('UPI', 'UPI'),
    ]

    certificate_request = models.ForeignKey(CertificateRequest, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.certificate_request.application_number} - {self.payment_status}"


class Certificate(models.Model):
    """Issued certificates"""
    certificate_request = models.OneToOneField(CertificateRequest, on_delete=models.CASCADE)
    certificate_number = models.CharField(max_length=50, unique=True, blank=True)
    issued_by = models.ForeignKey(Authority, on_delete=models.CASCADE)
    certificate_file = models.FileField(upload_to="issued_certificates")
    service_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Final service fee")
    issue_date = models.DateTimeField(auto_now_add=True)
    validity_period = models.CharField(max_length=100, blank=True, null=True, help_text="e.g., Lifetime, 5 years")
    qr_code = models.ImageField(upload_to="certificate_qr", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            # Generate certificate number: CERT-TYPE-YYYY-NNNN
            year = datetime.now().year
            cert_type = self.certificate_request.certificate_type.name[:4].upper()
            count = Certificate.objects.filter(
                certificate_number__startswith=f'CERT-{cert_type}-{year}'
            ).count() + 1
            self.certificate_number = f'CERT-{cert_type}-{year}-{count:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.certificate_number}"

    class Meta:
        ordering = ['-issue_date']


class Feedback(models.Model):
    """Customer feedback - redesigned for certificate system"""
    FEEDBACK_TYPE_CHOICES = [
        ('Service', 'Service Quality'),
        ('Authority', 'Authority Performance'),
        ('System', 'System/Website'),
        ('General', 'General Feedback'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    certificate_request = models.ForeignKey(
        CertificateRequest, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Leave blank for general feedback"
    )
    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_TYPE_CHOICES)
    message = models.TextField()
    rating = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Rating from 1 to 5"
    )
    admin_reply = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.certificate_request:
            return f"Feedback for {self.certificate_request.application_number}"
        return f"General Feedback by {self.customer.name}"

    class Meta:
        ordering = ['-created_at']

class Scheme(models.Model):
    """Government schemes available for citizens"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    eligibility = models.TextField()
    benefits = models.TextField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class SchemeApplication(models.Model):
    """Citizen applications for schemes"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Verified', 'Verified'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    scheme = models.ForeignKey(Scheme, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    application_number = models.CharField(max_length=50, unique=True, blank=True)
    documents = models.FileField(upload_to="scheme_documents")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True, null=True)
    applied_date = models.DateTimeField(auto_now_add=True)
    verified_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.application_number:
            year = datetime.now().year
            count = SchemeApplication.objects.filter(
                application_number__startswith=f'SCH-{year}'
            ).count() + 1
            self.application_number = f'SCH-{year}-{count:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.application_number} - {self.scheme.name}"


class News(models.Model):
    """News and announcements about schemes and projects"""
    title = models.CharField(max_length=300)
    content = models.TextField()
    image = models.ImageField(upload_to="news_images", null=True, blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "News"


class Complaint(models.Model):
    """Citizen complaints system"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Resolved', 'Resolved'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reply = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Complaint: {self.subject} by {self.customer.name}"


class AdminNotice(models.Model):
    """Notices from Admin to Staff/Authorities"""
    title = models.CharField(max_length=300)
    message = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
