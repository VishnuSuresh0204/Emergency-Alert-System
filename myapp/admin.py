from django.contrib import admin
from .models import Login, Authority, CertificateType, CertificateRequest, Payment, Certificate, Customer, Feedback, Scheme, SchemeApplication, News, Complaint, AdminNotice

# Register your models here.
admin.site.register(Login)
admin.site.register(Authority)
admin.site.register(CertificateType)
admin.site.register(CertificateRequest)
admin.site.register(Payment)
admin.site.register(Certificate)
admin.site.register(Customer)
admin.site.register(Feedback)
admin.site.register(Scheme)
admin.site.register(SchemeApplication)
admin.site.register(News)
admin.site.register(Complaint)
admin.site.register(AdminNotice)