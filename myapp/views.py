from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Q, Sum, Count
from datetime import datetime
from django.utils import timezone

# ==========================================
# PUBLIC VIEWS
# ==========================================

def index(request):
    return render(request, 'index.html')

def register_public(request):
    if request.method == "POST":
        u = request.POST['username']
        p = request.POST['password']
        f = request.POST['fname']
        e = request.POST['email']
        ph = request.POST['phone']
        add = request.POST['address']
        dob = request.POST['dob']
        aadhar = request.POST['aadhar']
        
        try:
            user = Login.objects.create_user(username=u, password=p, userType='customer', viewPass=p)
            Customer.objects.create(
                loginid=user,
                name=f,
                email=e,
                phone=ph,
                address=add,
                date_of_birth=dob,
                aadhar_number=aadhar
            )
            messages.success(request, "Registration Successful! Please Login.")
            return redirect('/login/')
        except Exception as e:
            messages.error(request, f"Registration Failed: {e}")
            return redirect('/register/')
            
    return render(request, 'customer_register.html')

def login_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        user = authenticate(request, username=u, password=p)
        
        if user is not None:
            if user.userType == 'admin':
                login(request, user)
                request.session['lid'] = user.id
                return redirect('/admin_home/')
                
            elif user.userType == 'authority':
                try:
                    auth = Authority.objects.get(loginid=user)
                    if auth.status == 'active':
                        login(request, user)
                        request.session['lid'] = user.id
                        return redirect('/authority_home/')
                    else:
                        messages.error(request, f"Account is {auth.status}")
                        return redirect('/login/')
                except Authority.DoesNotExist:
                    messages.error(request, "Authority profile not found")
                    return redirect('/login/')
                    
            elif user.userType == 'customer':
                try:
                    cust = Customer.objects.get(loginid=user)
                    if cust.status == 'active':
                        login(request, user)
                        request.session['lid'] = user.id
                        return redirect('/customer_home/')
                    else:
                        messages.error(request, f"Account is {cust.status}")
                        return redirect('/login/')
                except Customer.DoesNotExist:
                    messages.error(request, "Customer profile not found")
                    return redirect('/login/')
            else:
                messages.error(request, "Invalid User Type")
                return redirect('/login/')
        else:
            messages.error(request, "Invalid username or password")
            return redirect('/login/')
            
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

# ==========================================
# ADMIN VIEWS
# ==========================================

@login_required
def admin_home(request):
    if request.user.userType != 'admin': return redirect('/')
    
    # Overview Stats
    total_authorities = Authority.objects.filter(status='active').count()
    total_customers = Customer.objects.count()
    total_requests = CertificateRequest.objects.count()
    total_issued = Certificate.objects.count()
    total_revenue = Payment.objects.filter(payment_status='Completed').aggregate(total=Sum('amount'))['total'] or 0
    total_cert_types = CertificateType.objects.filter(is_active=True).count()
    
    # Request Status Breakdown
    stats_by_status = CertificateRequest.objects.values('status').annotate(total=Count('id'))
    status_counts = {item['status']: item['total'] for item in stats_by_status}
    
    # Recent Activities
    recent_requests = CertificateRequest.objects.all().order_by('-applied_date')[:6]
    recent_feedbacks = Feedback.objects.all().order_by('-created_at')[:5]
    
    # Top Certificate Types
    top_services = CertificateRequest.objects.values('certificate_type__name').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    context = {
        'total_authorities': total_authorities,
        'total_customers': total_customers,
        'total_requests': total_requests,
        'total_issued': total_issued,
        'total_revenue': total_revenue,
        'total_cert_types': total_cert_types,
        'status_counts': status_counts,
        'recent_requests': recent_requests,
        'recent_feedbacks': recent_feedbacks,
        'top_services': top_services,
    }
    return render(request, 'ADMIN/admin_home.html', context)

@login_required
def admin_add_authority(request):
    if request.user.userType != 'admin': return redirect('/')
    
    if request.method == "POST":
        u = request.POST['username']
        p = request.POST['password']
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        designation = request.POST['designation']
        address = request.POST['address']
        
        try:
            user = Login.objects.create_user(username=u, password=p, userType='authority', viewPass=p)
            
            authority = Authority.objects.create(
                loginid=user,
                name=name,
                email=email,
                phone=phone,
                designation=designation,
                office_address=address
            )
            
            if 'profile_pic' in request.FILES:
                authority.profile_pic = request.FILES['profile_pic']
                authority.save()
                
            messages.success(request, "Authority Added Successfully")
            return redirect('/admin_view_authorities/')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            
    return render(request, 'ADMIN/add_authority.html')

@login_required
def admin_view_authorities(request):
    if request.user.userType != 'admin': return redirect('/')
    authorities = Authority.objects.all()
    return render(request, 'ADMIN/view_authorities.html', {'authorities': authorities})

@login_required
def admin_edit_authority(request):
    if request.user.userType != 'admin': return redirect('/')
    
    auth_id = request.GET.get('id')
    authority = get_object_or_404(Authority, id=auth_id)
    
    if request.method == "POST":
        authority.name = request.POST['name']
        authority.email = request.POST['email']
        authority.phone = request.POST['phone']
        authority.designation = request.POST['designation']
        authority.office_address = request.POST['address']
        authority.status = request.POST['status']
        
        if 'profile_pic' in request.FILES:
            authority.profile_pic = request.FILES['profile_pic']
            
        authority.save()
        messages.success(request, "Authority Updated Successfully")
        return redirect('/admin_view_authorities/')
        
    return render(request, 'ADMIN/edit_authority.html', {'authority': authority})

@login_required
def admin_block_authority(request):
    if request.user.userType != 'admin': return redirect('/')
    auth_id = request.GET.get('id')
    authority = get_object_or_404(Authority, id=auth_id)
    authority.status = 'inactive'
    authority.save()
    messages.warning(request, f"Authority {authority.name} has been blocked.")
    return redirect('/admin_view_authorities/')

@login_required
def admin_unblock_authority(request):
    if request.user.userType != 'admin': return redirect('/')
    auth_id = request.GET.get('id')
    authority = get_object_or_404(Authority, id=auth_id)
    authority.status = 'active'
    authority.save()
    messages.success(request, f"Authority {authority.name} has been unblocked.")
    return redirect('/admin_view_authorities/')

@login_required
def admin_view_requests(request):
    if request.user.userType != 'admin': return redirect('/')
    
    requests = CertificateRequest.objects.all().order_by('-applied_date')
    authorities = Authority.objects.filter(status='active')
    
    status_filter = request.GET.get('status')
    if status_filter:
        requests = requests.filter(status=status_filter)
        
    return render(request, 'ADMIN/view_requests.html', {
        'requests': requests,
        'authorities': authorities
    })

@login_required
def admin_forward_request(request):
    if request.user.userType != 'admin': return redirect('/')
    
    req_id = request.POST.get('request_id')
    auth_id = request.POST.get('authority_id')
    
    cert_req = get_object_or_404(CertificateRequest, id=req_id)
    authority = get_object_or_404(Authority, id=auth_id)
    
    cert_req.assigned_authority = authority
    cert_req.status = 'Forwarded'
    cert_req.forwarded_date = datetime.now()
    cert_req.save()
    
    messages.success(request, f"Request forwarded to {authority.name}")
    return redirect('/admin_view_requests/')

@login_required
def admin_view_feedback(request):
    if request.user.userType != 'admin': return redirect('/')
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'ADMIN/view_feedback.html', {'feedbacks': feedbacks})

@login_required
def admin_reply_feedback(request):
    if request.user.userType != 'admin': return redirect('/')
    
    feedback_id = request.POST.get('feedback_id')
    reply = request.POST.get('reply')
    
    feedback = get_object_or_404(Feedback, id=feedback_id)
    feedback.admin_reply = reply
    feedback.save()
    
    messages.success(request, "Reply sent successfully")
    return redirect('/admin_view_feedback/')

@login_required
def admin_view_customers(request):
    if request.user.userType != 'admin': return redirect('/')
    customers = Customer.objects.all()
    return render(request, 'ADMIN/view_customers.html', {'customers': customers})

@login_required
def admin_block_customer(request):
    if request.user.userType != 'admin': return redirect('/')
    cust_id = request.GET.get('id')
    customer = get_object_or_404(Customer, id=cust_id)
    customer.status = 'inactive'
    customer.save()
    messages.warning(request, f"Customer {customer.name} has been blocked.")
    return redirect('/admin_view_customers/')

@login_required
def admin_unblock_customer(request):
    if request.user.userType != 'admin': return redirect('/')
    cust_id = request.GET.get('id')
    customer = get_object_or_404(Customer, id=cust_id)
    customer.status = 'active'
    customer.save()
    messages.success(request, f"Customer {customer.name} has been unblocked.")
    return redirect('/admin_view_customers/')

@login_required
def admin_manage_schemes(request):
    if request.user.userType != 'admin': return redirect('/')
    schemes = Scheme.objects.all()
    return render(request, 'ADMIN/manage_schemes.html', {'schemes': schemes})

@login_required
def admin_add_scheme(request):
    if request.user.userType != 'admin': return redirect('/')
    if request.method == "POST":
        name = request.POST['name']
        desc = request.POST['description']
        eligibility = request.POST['eligibility']
        benefits = request.POST['benefits']
        start_date = request.POST.get('start_date') or None
        end_date = request.POST.get('end_date') or None
        Scheme.objects.create(
            name=name, 
            description=desc, 
            eligibility=eligibility, 
            benefits=benefits,
            start_date=start_date,
            end_date=end_date
        )
        messages.success(request, "Scheme Added Successfully")
        return redirect('/admin_manage_schemes/')
    return render(request, 'ADMIN/add_scheme.html')

@login_required
def admin_edit_scheme(request):
    if request.user.userType != 'admin': return redirect('/')
    scheme_id = request.GET.get('id')
    scheme = get_object_or_404(Scheme, id=scheme_id)
    if request.method == "POST":
        scheme.name = request.POST['name']
        scheme.description = request.POST['description']
        scheme.eligibility = request.POST['eligibility']
        scheme.benefits = request.POST['benefits']
        scheme.start_date = request.POST.get('start_date') or None
        scheme.end_date = request.POST.get('end_date') or None
        scheme.is_active = 'is_active' in request.POST
        scheme.save()
        messages.success(request, "Scheme Updated Successfully")
        return redirect('/admin_manage_schemes/')
    return render(request, 'ADMIN/edit_scheme.html', {
        'scheme': scheme,
        'is_active_checked': 'checked' if scheme.is_active else ''
    })

@login_required
def admin_view_news(request):
    if request.user.userType != 'admin': return redirect('/')
    news_items = News.objects.all().order_by('-date_posted')
    return render(request, 'ADMIN/view_news.html', {'news_items': news_items})

@login_required
def admin_add_news(request):
    if request.user.userType != 'admin': return redirect('/')
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        news = News.objects.create(title=title, content=content)
        if 'image' in request.FILES:
            news.image = request.FILES['image']
            news.save()
        messages.success(request, "News Added Successfully")
        return redirect('/admin_view_news/')
    return render(request, 'ADMIN/add_news.html')

@login_required
def admin_edit_news(request):
    if request.user.userType != 'admin': return redirect('/')
    id = request.GET.get('id')
    news = get_object_or_404(News, id=id)
    if request.method == "POST":
        news.title = request.POST['title']
        news.content = request.POST['content']
        if 'image' in request.FILES:
            news.image = request.FILES['image']
        news.is_active = 'is_active' in request.POST
        news.save()
        messages.success(request, "News Updated Successfully")
        return redirect('/admin_view_news/')
    
    context = {
        'news': news,
        'is_active_checked': 'checked' if news.is_active else ''
    }
    return render(request, 'ADMIN/edit_news.html', context)

@login_required
def admin_toggle_news_status(request):
    if request.user.userType != 'admin': return redirect('/')
    id = request.GET.get('id')
    news = get_object_or_404(News, id=id)
    news.is_active = not news.is_active
    news.save()
    status = "Published" if news.is_active else "Hidden"
    messages.success(request, f"News status updated to {status}")
    return redirect('/admin_view_news/')

@login_required
def admin_total_reports(request):
    if request.user.userType != 'admin': return redirect('/')
    
    report_data = {
        'total_schemes': Scheme.objects.count(),
        'total_scheme_apps': SchemeApplication.objects.count(),
        'scheme_apps_by_status': SchemeApplication.objects.values('status').annotate(count=Count('id')),
        'total_complaints': Complaint.objects.count(),
        'complaints_by_status': Complaint.objects.values('status').annotate(count=Count('id')),
        'total_news': News.objects.count(),
        'total_customers': Customer.objects.count(),
        'total_authorities': Authority.objects.count(),
    }
    return render(request, 'ADMIN/reports.html', report_data)

@login_required
def admin_add_notice(request):
    if request.user.userType != 'admin': return redirect('/')
    if request.method == "POST":
        title = request.POST['title']
        message = request.POST['message']
        AdminNotice.objects.create(title=title, message=message)
        messages.success(request, "Notice Issued to Staff")
        return redirect('/admin_home/')
    return render(request, 'ADMIN/add_notice.html')

# ==========================================
# AUTHORITY VIEWS
# ==========================================

@login_required
def authority_home(request):
    if request.user.userType != 'authority': return redirect('/')
    
    authority = get_object_or_404(Authority, loginid=request.user)
    if authority.status != 'active':
        messages.error(request, f"Account is {authority.status}")
        return redirect('/login/')
    
    assigned_requests = CertificateRequest.objects.filter(assigned_authority=authority)
    
    context = {
        'authority': authority,
        'pending_requests': assigned_requests.filter(Q(status='Forwarded') | Q(status='Under Review')).count(),
        'approved_requests': assigned_requests.filter(status='Approved').count(),
        'completed_requests': assigned_requests.filter(status='Issued').count(),
    }
    return render(request, 'AUTHORITY/authority_home.html', context)

@login_required
def authority_view_requests(request):
    if request.user.userType != 'authority': return redirect('/')
    
    authority = get_object_or_404(Authority, loginid=request.user)
    if authority.status != 'active':
        messages.error(request, f"Account is {authority.status}")
        return redirect('/login/')
        
    requests = CertificateRequest.objects.filter(assigned_authority=authority).order_by('-forwarded_date')
    
    return render(request, 'AUTHORITY/view_requests.html', {'requests': requests})

@login_required
def authority_request_detail(request):
    if request.user.userType != 'authority': return redirect('/')
    
    authority = get_object_or_404(Authority, loginid=request.user)
    if authority.status != 'active':
        messages.error(request, f"Account is {authority.status}")
        return redirect('/login/')
    
    req_id = request.GET.get('id')
    cert_req = get_object_or_404(CertificateRequest, id=req_id)
    
    if request.method == "POST":
        action = request.POST.get('action')
        remarks = request.POST.get('remarks')
        
        if action == 'approve':
            cert_req.status = 'Approved'
        elif action == 'reject':
            cert_req.status = 'Rejected'
        elif action == 'review':
            cert_req.status = 'Under Review'
            
        cert_req.remarks = remarks
        cert_req.processed_date = datetime.now()
        cert_req.save()
        
        messages.success(request, f"Request status updated to {cert_req.status}")
        return redirect('/authority_view_requests/')
        
    return render(request, 'AUTHORITY/request_detail.html', {'cert_request': cert_req})

@login_required
def authority_issue_certificate(request):
    if request.user.userType != 'authority': return redirect('/')
    
    authority = get_object_or_404(Authority, loginid=request.user)
    if authority.status != 'active':
        messages.error(request, f"Account is {authority.status}")
        return redirect('/login/')
    
    req_id = request.GET.get('id')
    cert_req = get_object_or_404(CertificateRequest, id=req_id)
    
    if request.method == "POST":
        amount = request.POST.get('amount')
        validity = request.POST.get('validity')
        
        if 'certificate_file' in request.FILES:
            cert_file = request.FILES['certificate_file']
            
            # Create Certificate
            certificate = Certificate.objects.create(
                certificate_request=cert_req,
                issued_by=authority,
                certificate_file=cert_file,
                service_amount=amount,
                validity_period=validity
            )
            
            # Update Request Status
            cert_req.status = 'Issued'
            cert_req.save()
            
            messages.success(request, f"Certificate Issued Successfully. Certificate No: {certificate.certificate_number}")
            return redirect('/authority_view_requests/')
        else:
            messages.error(request, "Please upload certificate file")
            
    return render(request, 'AUTHORITY/issue_certificate.html', {'cert_request': cert_req})

@login_required
def authority_issued_certificates(request):
    if request.user.userType != 'authority': return redirect('/')
    
    authority = get_object_or_404(Authority, loginid=request.user)
    if authority.status != 'active':
        messages.error(request, f"Account is {authority.status}")
        return redirect('/login/')
        
    certificates = Certificate.objects.filter(issued_by=authority)
    
    return render(request, 'AUTHORITY/issued_certificates.html', {'certificates': certificates})

@login_required
def staff_view_scheme_applications(request):
    if request.user.userType != 'authority': return redirect('/')
    applications = SchemeApplication.objects.all().order_by('-applied_date')
    return render(request, 'AUTHORITY/scheme_applications.html', {'applications': applications})

@login_required
def staff_verify_scheme_application(request):
    if request.user.userType != 'authority': return redirect('/')
    app_id = request.GET.get('id')
    application = get_object_or_404(SchemeApplication, id=app_id)
    if request.method == "POST":
        status = request.POST['status']
        remarks = request.POST['remarks']
        application.status = status
        application.remarks = remarks
        if status == 'Verified':
            application.verified_date = datetime.now()
        application.save()
        messages.success(request, f"Application {status} Successfully")
        return redirect('/staff_view_scheme_applications/')
    return render(request, 'AUTHORITY/verify_scheme.html', {'application': application})

@login_required
def staff_view_complaints(request):
    if request.user.userType != 'authority': return redirect('/')
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, 'AUTHORITY/view_complaints.html', {'complaints': complaints})

@login_required
def staff_reply_complaint(request):
    if request.user.userType != 'authority': return redirect('/')
    comp_id = request.POST.get('complaint_id')
    reply = request.POST.get('reply')
    complaint = get_object_or_404(Complaint, id=comp_id)
    complaint.reply = reply
    complaint.status = 'Resolved'
    complaint.resolved_at = datetime.now()
    complaint.save()
    messages.success(request, "Reply sent and complaint marked as Resolved")
    return redirect('/staff_view_complaints/')

@login_required
def staff_view_notices(request):
    if request.user.userType != 'authority': return redirect('/')
    notices = AdminNotice.objects.all().order_by('-date_posted')
    return render(request, 'AUTHORITY/view_notices.html', {'notices': notices})

# ==========================================
# CUSTOMER VIEWS
# ==========================================

@login_required
def customer_home(request):
    if request.user.userType != 'customer': return redirect('/')
    return render(request, 'CUSTOMER/customer_home.html')

@login_required
def customer_apply_certificate(request):
    if request.user.userType != 'customer': return redirect('/')
    
    cert_types = CertificateType.objects.filter(is_active=True)
    customer = Customer.objects.get(loginid=request.user)
    
    if request.method == "POST":
        cert_type_id = request.POST['cert_type']
        cert_type = get_object_or_404(CertificateType, id=cert_type_id)
        
        name = request.POST['name']
        father = request.POST['father_name']
        address = request.POST['address']
        dob = request.POST['dob']
        details = request.POST['details']
        
        req = CertificateRequest.objects.create(
            customer=customer,
            certificate_type=cert_type,
            applicant_name=name,
            applicant_father_name=father,
            applicant_address=address,
            applicant_dob=dob,
            additional_details=details
        )
        
        if 'doc1' in request.FILES: req.document1 = request.FILES['doc1']
        if 'doc2' in request.FILES: req.document2 = request.FILES['doc2']
        if 'doc3' in request.FILES: req.document3 = request.FILES['doc3']
        req.save()
        
        messages.success(request, f"Application Submitted Successfully. Your Application No is: {req.application_number}")
        return redirect('/customer_applications/')
        
    return render(request, 'CUSTOMER/apply_certificate.html', {'cert_types': cert_types, 'customer': customer})

@login_required
def customer_view_applications(request):
    if request.user.userType != 'customer': return redirect('/')
    
    customer = Customer.objects.get(loginid=request.user)
    applications = CertificateRequest.objects.filter(customer=customer).order_by('-applied_date')
    
    return render(request, 'CUSTOMER/view_applications.html', {'applications': applications})

@login_required
def customer_application_detail(request):
    if request.user.userType != 'customer': return redirect('/')
    
    app_id = request.GET.get('id')
    application = get_object_or_404(CertificateRequest, id=app_id)
    
    # Check if certificate exists
    certificate = None
    if hasattr(application, 'certificate'):
        certificate = application.certificate
        
    return render(request, 'CUSTOMER/application_detail.html', {
        'application': application,
        'certificate': certificate
    })

@login_required
def customer_payment(request):
    if request.user.userType != 'customer': return redirect('/')
    
    app_id = request.GET.get('id')
    application = get_object_or_404(CertificateRequest, id=app_id)
    
    if request.method == "POST":
        amount = request.POST['amount']
        method = request.POST['payment_method']
        
        Payment.objects.create(
            certificate_request=application,
            amount=amount,
            payment_method=method,
            payment_status='Completed',
            transaction_id=f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        messages.success(request, "Payment Successful")
        return redirect(f'/customer_application_detail/?id={application.id}')
        
    return render(request, 'CUSTOMER/payment.html', {'application': application})

@login_required
def customer_add_feedback(request):
    if request.user.userType != 'customer': return redirect('/')
    
    customer = Customer.objects.get(loginid=request.user)
    
    if request.method == "POST":
        fb_type = request.POST['type']
        message = request.POST['message']
        rating = request.POST['rating']
        
        Feedback.objects.create(
            customer=customer,
            feedback_type=fb_type,
            message=message,
            rating=rating
        )
        messages.success(request, "Feedback Submitted Successfully")
        return redirect('/customer_view_feedback/')
        
    return render(request, 'CUSTOMER/add_feedback.html')

@login_required
def customer_view_feedback(request):
    if request.user.userType != 'customer': return redirect('/')
    
    customer = Customer.objects.get(loginid=request.user)
    feedbacks = Feedback.objects.filter(customer=customer).order_by('-created_at')
    
    return render(request, 'CUSTOMER/view_feedback.html', {'feedbacks': feedbacks})

@login_required
def customer_view_schemes(request):
    if request.user.userType != 'customer': return redirect('/')
    schemes = Scheme.objects.filter(is_active=True)
    today = timezone.now().date()
    
    # Calculate status in python to avoid template tag issues
    for s in schemes:
        if s.start_date and today < s.start_date:
            s.app_status = 'upcoming'
        elif s.end_date and today > s.end_date:
            s.app_status = 'ended'
        else:
            s.app_status = 'open'
            
    return render(request, 'CUSTOMER/view_schemes.html', {'schemes': schemes, 'today': today})

@login_required
def customer_apply_scheme(request):
    if request.user.userType != 'customer': return redirect('/')
    scheme_id = request.GET.get('id')
    scheme = get_object_or_404(Scheme, id=scheme_id)
    customer = Customer.objects.get(loginid=request.user)
    
    today = timezone.now().date()
    
    # Date Validation
    if scheme.start_date and today < scheme.start_date:
        messages.error(request, f"Applications for {scheme.name} haven't started yet. Opening on {scheme.start_date}")
        return redirect('/customer_view_schemes/')
    
    if scheme.end_date and today > scheme.end_date:
        messages.error(request, f"Applications for {scheme.name} ended on {scheme.end_date}")
        return redirect('/customer_view_schemes/')
    
    if request.method == "POST":
        app = SchemeApplication.objects.create(
            scheme=scheme,
            customer=customer,
        )
        if 'documents' in request.FILES:
            app.documents = request.FILES['documents']
            app.save()
        messages.success(request, f"Applied for {scheme.name} successfully. App No: {app.application_number}")
        return redirect('/customer_scheme_status/')
    return render(request, 'CUSTOMER/apply_scheme.html', {'scheme': scheme})

@login_required
def customer_scheme_status(request):
    if request.user.userType != 'customer': return redirect('/')
    customer = Customer.objects.get(loginid=request.user)
    applications = SchemeApplication.objects.filter(customer=customer).order_by('-applied_date')
    return render(request, 'CUSTOMER/my_schemes.html', {'applications': applications})

@login_required
def customer_scheme_application_detail(request):
    if request.user.userType != 'customer': return redirect('/')
    app_id = request.GET.get('id')
    application = get_object_or_404(SchemeApplication, id=app_id)
    return render(request, 'CUSTOMER/scheme_application_detail.html', {'application': application})

@login_required
def customer_add_complaint(request):
    if request.user.userType != 'customer': return redirect('/')
    if request.method == "POST":
        customer = Customer.objects.get(loginid=request.user)
        subject = request.POST['subject']
        desc = request.POST['description']
        Complaint.objects.create(customer=customer, subject=subject, description=desc)
        messages.success(request, "Complaint submitted successfully")
        return redirect('/customer_view_complaints/')
    return render(request, 'CUSTOMER/add_complaint.html')

@login_required
def customer_view_complaints(request):
    if request.user.userType != 'customer': return redirect('/')
    customer = Customer.objects.get(loginid=request.user)
    complaints = Complaint.objects.filter(customer=customer).order_by('-created_at')
    return render(request, 'CUSTOMER/view_complaints.html', {'complaints': complaints})

@login_required
def customer_view_news(request):
    if request.user.userType != 'customer': return redirect('/')
    news_items = News.objects.filter(is_active=True).order_by('-date_posted')
    return render(request, 'CUSTOMER/view_news.html', {'news_items': news_items})
