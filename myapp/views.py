from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.db.models import Q

# --- Public Views ---

def index(request):
    alerts = EmergencyAlert.objects.filter(is_active=True).order_by('-created_at')[:5]
    return render(request, 'index.html', {'alerts': alerts})

def login_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            login(request, user)
            if user.userType == "admin":
                return redirect('admin_home')
            elif user.userType == "staff":
                return redirect('staff_home')
            elif user.userType == "volunteer":
                return redirect('volunteer_home')
            elif user.userType == "user":
                return redirect('citizen_home')
        messages.error(request, "Invalid Credentials")
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def register_citizen(request):
    districts = District.objects.all()
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('name')
        e = request.POST.get('email')
        ph = request.POST.get('phone')
        ad = request.POST.get('address')
        di = request.POST.get('district')
        pic = request.FILES.get('profile_pic')
        
        if Login.objects.filter(username=u).exists():
            messages.error(request, "Username already exists")
        else:
            log = Login.objects.create_user(username=u, password=p, userType="user", viewPass=p)
            district = District.objects.get(id=di)
            Citizen.objects.create(loginid=log, name=n, email=e, phone=ph, address=ad, district=district, profile_pic=pic)
            messages.success(request, "Registration Successful")
            return redirect('login')
    return render(request, 'register_citizen.html', {'districts': districts})

def register_volunteer(request):
    districts = District.objects.all()
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('name')
        e = request.POST.get('email')
        ph = request.POST.get('phone')
        sk = request.POST.get('skills')
        di = request.POST.get('district')
        pic = request.FILES.get('profile_pic')
        
        if Login.objects.filter(username=u).exists():
            messages.error(request, "Username already exists")
        else:
            log = Login.objects.create_user(username=u, password=p, userType="volunteer", viewPass=p)
            district = District.objects.get(id=di)
            Volunteer.objects.create(loginid=log, name=n, email=e, phone=ph, skills=sk, district=district, profile_pic=pic)
            messages.success(request, "Registration Successful. Waiting for Admin Approval.")
            return redirect('login')
    return render(request, 'register_volunteer.html', {'districts': districts})

# --- Admin Views ---

def admin_home(request):
    stats = {
        'districts': District.objects.count(),
        'staff': Staff.objects.count(),
        'volunteers': Volunteer.objects.count(),
        'active_alerts': EmergencyAlert.objects.filter(is_active=True).count(),
        'pending_reports': EmergencyReport.objects.filter(status='Pending').count(),
    }
    return render(request, 'ADMIN/admin_home.html', stats)

def admin_manage_districts(request):
    districts = District.objects.all()
    return render(request, 'ADMIN/manage_districts.html', {'districts': districts})

def admin_add_district(request):
    if request.method == "POST":
        n = request.POST.get('name')
        d = request.POST.get('description')
        District.objects.create(name=n, description=d)
        messages.success(request, "District Added")
        return redirect('admin_manage_districts')
    return render(request, 'ADMIN/add_district.html')

def admin_manage_staff(request):
    staff = Staff.objects.all()
    return render(request, 'ADMIN/manage_staff.html', {'staff': staff})

def admin_add_staff(request):
    districts = District.objects.all()
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('name')
        e = request.POST.get('email')
        ph = request.POST.get('phone')
        di = request.POST.get('district')
        des = request.POST.get('designation')
        pic = request.FILES.get('profile_pic')
        
        log = Login.objects.create_user(username=u, password=p, userType="staff", viewPass=p)
        district = District.objects.get(id=di)
        Staff.objects.create(loginid=log, name=n, email=e, phone=ph, district=district, designation=des, profile_pic=pic)
        messages.success(request, "Staff Added")
        return redirect('admin_manage_staff')
    return render(request, 'ADMIN/add_staff.html', {'districts': districts})

def admin_approve_volunteers(request):
    volunteers = Volunteer.objects.filter(status="Pending")
    if request.method == "POST":
        vid = request.POST.get('vid')
        action = request.POST.get('action')
        v = Volunteer.objects.get(id=vid)
        if action == "approve":
            v.status = "Approved"
            v.save()
            messages.success(request, "Volunteer Approved")
        else:
            v.loginid.delete() # Deletes user login as well
            messages.info(request, "Volunteer Rejected")
        return redirect('admin_approve_volunteers')
    return render(request, 'ADMIN/approve_volunteers.html', {'volunteers': volunteers})

def admin_manage_emergency_types(request):
    types = EmergencyType.objects.all()
    return render(request, 'ADMIN/manage_emergency_types.html', {'types': types})

def admin_add_emergency_type(request):
    if request.method == "POST":
        n = request.POST.get('name')
        d = request.POST.get('description')
        ic = request.FILES.get('icon')
        EmergencyType.objects.create(name=n, description=d, icon=ic)
        return redirect('admin_manage_emergency_types')
    return render(request, 'ADMIN/add_emergency_type.html')

def admin_view_all_reports(request):
    reports = EmergencyReport.objects.all().order_by('-reported_at')
    return render(request, 'ADMIN/view_all_reports.html', {'reports': reports})

def admin_send_alert(request):
    districts = District.objects.all()
    if request.method == "POST":
        ti = request.POST.get('title')
        msg = request.POST.get('message')
        lv = request.POST.get('level')
        di = request.POST.get('district')
        district = District.objects.get(id=di)
        EmergencyAlert.objects.create(title=ti, message=msg, alert_level=lv, district=district, posted_by=request.user)
        messages.success(request, "Alert Sent to District Citizens")
        return redirect('admin_home')
    return render(request, 'ADMIN/send_alert.html', {'districts': districts})

def admin_view_feedback(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'ADMIN/view_feedback.html', {'feedbacks': feedbacks})

# --- Staff Views ---

def staff_home(request):
    staff = Staff.objects.get(loginid=request.user)
    reports = EmergencyReport.objects.filter(district=staff.district).order_by('-reported_at')[:5]
    return render(request, 'STAFF/staff_home.html', {'staff': staff, 'reports': reports})

def staff_view_reports(request):
    staff = Staff.objects.get(loginid=request.user)
    reports = EmergencyReport.objects.filter(district=staff.district).order_by('-reported_at')
    return render(request, 'STAFF/view_reports.html', {'reports': reports})

def staff_verify_report(request, report_id):
    report = get_object_or_404(EmergencyReport, id=report_id)
    if request.method == "POST":
        st = request.POST.get('status')
        rem = request.POST.get('remarks')
        report.status = st
        report.remarks = rem
        report.verified_by = Staff.objects.get(loginid=request.user)
        report.save()
        messages.success(request, "Report Verified and Status Updated")
        return redirect('staff_view_reports')
    return render(request, 'STAFF/verify_report.html', {'report': report})

def staff_view_rescue_requests(request):
    staff = Staff.objects.get(loginid=request.user)
    requests = RescueRequest.objects.filter(district=staff.district).order_by('-created_at')
    return render(request, 'STAFF/view_rescue_requests.html', {'requests': requests})

def staff_assign_volunteers(request, request_id):
    rescue_request = get_object_or_404(RescueRequest, id=request_id)
    volunteers = Volunteer.objects.filter(district=rescue_request.district, status="Approved", availability_status="Available")
    if request.method == "POST":
        vids = request.POST.getlist('volunteers')
        rescue_request.assigned_volunteers.set(vids)
        rescue_request.status = "Assigned"
        rescue_request.save()
        messages.success(request, "Volunteers Assigned to Rescue Operation")
        return redirect('staff_view_rescue_requests')
    return render(request, 'STAFF/assign_volunteers.html', {'rescue_request': rescue_request, 'volunteers': volunteers})

def staff_update_situation(request, report_id):
    report = get_object_or_404(EmergencyReport, id=report_id)
    if request.method == "POST":
        st = request.POST.get('status')
        report.status = st
        report.save()
        return redirect('staff_view_reports')
    return render(request, 'STAFF/update_situation.html', {'report': report})

def staff_broadcast_alert(request):
    staff = Staff.objects.get(loginid=request.user)
    if request.method == "POST":
        ti = request.POST.get('title')
        msg = request.POST.get('message')
        lv = request.POST.get('level')
        EmergencyAlert.objects.create(title=ti, message=msg, alert_level=lv, district=staff.district, posted_by=request.user)
        messages.success(request, "District Alert Broadcasted")
        return redirect('staff_home')
    return render(request, 'STAFF/broadcast_alert.html')

# --- Volunteer Views ---

def volunteer_home(request):
    volunteer = Volunteer.objects.get(loginid=request.user)
    assignments = RescueRequest.objects.filter(assigned_volunteers=volunteer).order_by('-created_at')
    return render(request, 'VOLUNTEER/volunteer_home.html', {'volunteer': volunteer, 'assignments': assignments})

def volunteer_view_assignments(request):
    volunteer = Volunteer.objects.get(loginid=request.user)
    assignments = RescueRequest.objects.filter(assigned_volunteers=volunteer).order_by('-created_at')
    return render(request, 'VOLUNTEER/view_assignments.html', {'assignments': assignments})

def volunteer_update_status(request):
    volunteer = Volunteer.objects.get(loginid=request.user)
    if request.method == "POST":
        st = request.POST.get('status')
        volunteer.availability_status = st
        volunteer.save()
        messages.success(request, "Availability Updated")
    return redirect('volunteer_home')

def volunteer_view_emergency_map(request):
    # Mock map view
    return render(request, 'VOLUNTEER/view_map.html')

# --- Citizen Views ---

def citizen_home(request):
    citizen = Citizen.objects.get(loginid=request.user)
    alerts = EmergencyAlert.objects.filter(district=citizen.district, is_active=True).order_by('-created_at')
    return render(request, 'CITIZEN/citizen_home.html', {'citizen': citizen, 'alerts': alerts})

def citizen_report_emergency(request):
    types = EmergencyType.objects.all()
    citizen = Citizen.objects.get(loginid=request.user)
    if request.method == "POST":
        ty = request.POST.get('type')
        loc = request.POST.get('location')
        desc = request.POST.get('description')
        img = request.FILES.get('image')
        
        etype = EmergencyType.objects.get(id=ty)
        EmergencyReport.objects.create(user=citizen, emergency_type=etype, district=citizen.district, location_details=loc, description=desc, image=img)
        messages.success(request, "Emergency Reported. Authorities are notified.")
        return redirect('citizen_view_reports')
    return render(request, 'CITIZEN/report_emergency.html', {'types': types})

def citizen_view_reports(request):
    citizen = Citizen.objects.get(loginid=request.user)
    reports = EmergencyReport.objects.filter(user=citizen).order_by('-reported_at')
    return render(request, 'CITIZEN/view_reports.html', {'reports': reports})

def citizen_request_rescue(request, report_id):
    report = get_object_or_404(EmergencyReport, id=report_id)
    citizen = Citizen.objects.get(loginid=request.user)
    if request.method == "POST":
        cp = request.POST.get('contact_person')
        ph = request.POST.get('phone')
        num = request.POST.get('number')
        pri = request.POST.get('priority')
        msg = request.POST.get('message')
        
        RescueRequest.objects.create(report=report, user=citizen, district=citizen.district, contact_person=cp, contact_phone=ph, number_of_people=num, priority=pri, message=msg)
        messages.success(request, "Rescue Request Sent")
        return redirect('citizen_home')
    return render(request, 'CITIZEN/request_rescue.html', {'report': report})

def citizen_view_alerts(request):
    citizen = Citizen.objects.get(loginid=request.user)
    alerts = EmergencyAlert.objects.filter(district=citizen.district).order_by('-created_at')
    return render(request, 'CITIZEN/view_alerts.html', {'alerts': alerts})

def citizen_add_feedback(request):
    citizen = Citizen.objects.get(loginid=request.user)
    if request.method == "POST":
        sub = request.POST.get('subject')
        msg = request.POST.get('message')
        Feedback.objects.create(user=citizen, subject=sub, message=msg)
        messages.success(request, "Feedback Submitted")
        return redirect('citizen_home')
    return render(request, 'CITIZEN/add_feedback.html')
