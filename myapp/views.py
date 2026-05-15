from myapp.models import Citizen
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.db.models import Q

# --- Public Views ---

def index(request):
    logout(request)
    alerts = EmergencyAlert.objects.filter(is_active=True).order_by('-created_at')[:5]
    return render(request, 'index.html', {'alerts': alerts})

def login_view(request):
    if request.method == "POST":
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(username=u, password=p)
        if user:
            if user.userType == "admin" or user.is_superuser:
                login(request, user)
                request.session["lid"] = user.id
                return redirect("/admin_home")
            elif user.userType == "staff":
                s = Staff.objects.get(loginid=user)
                if s.status == "active":
                    login(request, user)
                    request.session["lid"] = user.id
                    return redirect("/staff_home")
                else:
                    messages.error(request, "Your account has been " + s.status)
                    return redirect("/login")
            elif user.userType == "volunteer":
                v = Volunteer.objects.get(loginid=user)
                if v.status == "Approved":
                    login(request, user)
                    request.session["lid"] = user.id
                    return redirect("/volunteer_home")
                else:
                    messages.error(request, "Account " + v.status + ". Wait for admin approval.")
                    return redirect("/login")
            elif user.userType == "user":
                login(request, user)
                request.session["lid"] = user.id
                return redirect("/citizen_home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("/login")
    return render(request, 'login.html')

def signout(request):
    logout(request)
    return redirect("/")

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
            return redirect("/register_citizen")

        log = Login.objects.create_user(username=u, password=p, userType="user", viewPass=p)
        district = District.objects.get(id=di)
        Citizen.objects.create(loginid=log, name=n, email=e, phone=ph, address=ad, district=district, profile_pic=pic)
        messages.success(request, "Registration Successful")
        return redirect("/login")
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
            return redirect("/register_volunteer")

        log = Login.objects.create_user(username=u, password=p, userType="volunteer", viewPass=p)
        district = District.objects.get(id=di)
        Volunteer.objects.create(loginid=log, name=n, email=e, phone=ph, skills=sk, district=district, profile_pic=pic)
        messages.success(request, "Registration Successful. Waiting for Admin Approval.")
        return redirect("/login")
    return render(request, 'register_volunteer.html', {'districts': districts})

# ================= ADMIN VIEWS =================

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
        return redirect("/admin_manage_districts")
    return render(request, 'ADMIN/add_district.html')

def admin_edit_district(request):
    id = request.GET.get("id")
    d = District.objects.get(id=id)
    if request.method == "POST":
        d.name = request.POST.get('name')
        d.description = request.POST.get('description')
        d.save()
        messages.success(request, "District Updated")
        return redirect("/admin_manage_districts")
    return render(request, 'ADMIN/edit_district.html', {'district': d})

def admin_delete_district(request):
    id = request.GET.get("id")
    District.objects.get(id=id).delete()
    messages.success(request, "District Deleted")
    return redirect("/admin_manage_districts")

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
        return redirect("/admin_manage_staff")
    return render(request, 'ADMIN/add_staff.html', {'districts': districts})

def admin_edit_staff(request):
    id = request.GET.get("id")
    s = Staff.objects.get(id=id)
    districts = District.objects.all()
    if request.method == "POST":
        s.name = request.POST.get('name')
        s.email = request.POST.get('email')
        s.phone = request.POST.get('phone')
        s.designation = request.POST.get('designation')
        di = request.POST.get('district')
        s.district = District.objects.get(id=di)
        
        if request.FILES.get('profile_pic'):
            s.profile_pic = request.FILES.get('profile_pic')
            
        s.save()
        messages.success(request, "Staff Details Updated")
        return redirect("/admin_manage_staff")
    return render(request, 'ADMIN/edit_staff.html', {'staff': s, 'districts': districts})

def admin_staff_status(request):
    id = request.GET.get("id")
    act = request.GET.get("act")
    s = Staff.objects.get(id=id)
    s.status = act
    s.save()
    messages.success(request, "Staff status updated to " + act)
    return redirect("/admin_manage_staff")

def admin_approve_volunteers(request):
    volunteers = Volunteer.objects.all()
    return render(request, 'ADMIN/approve_volunteers.html', {'volunteers': volunteers})

def admin_volunteer_action(request):
    id = request.GET.get("id")
    act = request.GET.get("act")
    v = Volunteer.objects.get(id=id)
    if act == "reject":
        v.loginid.delete()
        messages.info(request, "Volunteer Rejected")
    else:
        v.status = act
        v.save()
        messages.success(request, "Volunteer " + act)
    return redirect("/admin_approve_volunteers")

def admin_manage_emergency_types(request):
    types = EmergencyType.objects.all()
    return render(request, 'ADMIN/manage_emergency_types.html', {'types': types})

def admin_add_emergency_type(request):
    if request.method == "POST":
        n = request.POST.get('name')
        d = request.POST.get('description')
        ic = request.FILES.get('icon')
        EmergencyType.objects.create(name=n, description=d, icon=ic)
        messages.success(request, "Emergency Type Added")
        return redirect("/admin_manage_emergency_types")
    return render(request, 'ADMIN/add_emergency_type.html')

def admin_delete_emergency_type(request):
    id = request.GET.get("id")
    EmergencyType.objects.get(id=id).delete()
    messages.success(request, "Emergency Type Deleted")
    return redirect("/admin_manage_emergency_types")

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
        
        # Create notifications for all citizens in this district
        citizens = Citizen.objects.filter(district=district)
        for c in citizens:
            Notification.objects.create(user=c.loginid, message=f"ALERT: {ti}")
            
        messages.success(request, "Alert Sent to District Citizens")
        return redirect("/admin_view_alerts")
    return render(request, 'ADMIN/send_alert.html', {'districts': districts})

def admin_view_alerts(request):
    alerts = EmergencyAlert.objects.all().order_by('-created_at')
    return render(request, 'ADMIN/view_alerts.html', {'alerts': alerts})

def admin_delete_alert(request):
    id = request.GET.get("id")
    EmergencyAlert.objects.get(id=id).delete()
    messages.success(request, "Alert Deleted")
    return redirect("/admin_view_alerts")

def admin_view_feedback(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'ADMIN/view_feedback.html', {'feedbacks': feedbacks})

def admin_reply_feedback(request):
    id = request.GET.get("id")
    fb = Feedback.objects.get(id=id)
    if request.method == "POST":
        reply = request.POST.get("reply")
        fb.admin_reply = reply
        fb.save()
        messages.success(request, "Reply Sent")
        return redirect("/admin_view_feedback")
    return render(request, 'ADMIN/reply_feedback.html', {'feedback': fb})

def admin_view_citizens(request):
    citizens = Citizen.objects.all()
    return render(request, 'ADMIN/view_citizens.html', {'citizens': citizens})

# ================= STAFF VIEWS =================

def staff_home(request):
    staff = Staff.objects.get(loginid_id=request.session["lid"])
    reports = EmergencyReport.objects.filter(district=staff.district).order_by('-reported_at')[:5]
    return render(request, 'STAFF/staff_home.html', {'staff': staff, 'reports': reports})

def staff_view_reports(request):
    staff = Staff.objects.get(loginid_id=request.session["lid"])
    reports = EmergencyReport.objects.filter(district=staff.district).order_by('-reported_at')
    return render(request, 'STAFF/view_reports.html', {'reports': reports})

def staff_verify_report(request):
    id = request.GET.get("id")
    report = EmergencyReport.objects.get(id=id)
    if request.method == "POST":
        st = request.POST.get('status')
        rem = request.POST.get('remarks')
        report.status = st
        report.remarks = rem
        report.verified_by = Staff.objects.get(loginid_id=request.session["lid"])
        report.save()
        messages.success(request, "Report Verified and Status Updated")
        return redirect("/staff_view_reports")
    return render(request, 'STAFF/verify_report.html', {'report': report})

def staff_view_rescue_requests(request):
    staff = Staff.objects.get(loginid_id=request.session["lid"])
    reqs = RescueRequest.objects.filter(district=staff.district).order_by('-created_at')
    return render(request, 'STAFF/view_rescue_requests.html', {'requests': reqs})

def staff_assign_volunteers(request):
    id = request.GET.get("id")
    rescue_request = RescueRequest.objects.get(id=id)
    volunteers = Volunteer.objects.filter(district=rescue_request.district, status="Approved", availability_status="Available")
    if request.method == "POST":
        vids = request.POST.getlist('volunteers')
        rescue_request.assigned_volunteers.set(vids)
        rescue_request.status = "Assigned"
        rescue_request.save()
        
        # Notify assigned volunteers
        for vid in vids:
            v = Volunteer.objects.get(id=vid)
            Notification.objects.create(user=v.loginid, message=f"You have been assigned to a rescue mission for {rescue_request.contact_person}")
            
        messages.success(request, "Volunteers Assigned to Rescue Operation")
        return redirect("/staff_view_rescue_requests")
    return render(request, 'STAFF/assign_volunteers.html', {'rescue_request': rescue_request, 'volunteers': volunteers})

def staff_update_situation(request):
    id = request.GET.get("id")
    report = EmergencyReport.objects.get(id=id)
    if request.method == "POST":
        st = request.POST.get('status')
        report.status = st
        report.save()
        messages.success(request, "Situation Updated")
        return redirect("/staff_view_reports")
    return render(request, 'STAFF/update_situation.html', {'report': report})

def staff_post_news(request):
    staff = Staff.objects.get(loginid_id=request.session["lid"])
    if request.method == "POST":
        ti = request.POST.get('title')
        cont = request.POST.get('content')
        nt = request.POST.get('type')
        DistrictNews.objects.create(title=ti, content=cont, news_type=nt, district=staff.district, staff=staff)
        
        # Create notifications for all citizens in this district
        citizens = Citizen.objects.filter(district=staff.district)
        for c in citizens:
            Notification.objects.create(user=c.loginid, message=f"DISTRICT {nt.upper()}: {ti}")
            
        messages.success(request, f"District {nt} Posted")
        return redirect("/staff_home")
    return render(request, 'STAFF/post_news.html')

# ================= VOLUNTEER VIEWS =================

def volunteer_home(request):
    volunteer = Volunteer.objects.get(loginid_id=request.session["lid"])
    assignments = RescueRequest.objects.filter(assigned_volunteers=volunteer).order_by('-created_at')
    return render(request, 'VOLUNTEER/volunteer_home.html', {'volunteer': volunteer, 'assignments': assignments})

def volunteer_view_assignments(request):
    volunteer = Volunteer.objects.get(loginid_id=request.session["lid"])
    assignments = RescueRequest.objects.filter(assigned_volunteers=volunteer).order_by('-created_at')
    return render(request, 'VOLUNTEER/view_assignments.html', {'assignments': assignments})

def volunteer_update_status(request):
    volunteer = Volunteer.objects.get(loginid_id=request.session["lid"])
    if request.method == "POST":
        st = request.POST.get('status')
        volunteer.availability_status = st
        volunteer.save()
        messages.success(request, "Availability Updated")
    return redirect("/volunteer_home")

def volunteer_update_rescue(request):
    id = request.GET.get("id")
    rescue = RescueRequest.objects.get(id=id)
    if request.method == "POST":
        st = request.POST.get('status')
        rescue.status = st
        rescue.save()
        messages.success(request, "Rescue Status Updated")
    return redirect("/volunteer_view_assignments")

def volunteer_view_emergency_map(request):
    volunteer = Volunteer.objects.get(loginid_id=request.session["lid"])
    reports = EmergencyReport.objects.filter(district=volunteer.district).exclude(status='Resolved')
    return render(request, 'VOLUNTEER/view_map.html', {'reports': reports})

# ================= CITIZEN VIEWS =================

def citizen_home(request):
    citizen = Citizen.objects.get(loginid_id=request.session["lid"])
    alerts = EmergencyAlert.objects.filter(district=citizen.district, is_active=True).order_by('-created_at')
    return render(request, 'CITIZEN/citizen_home.html', {'citizen': citizen, 'alerts': alerts})

def citizen_report_emergency(request):
    types = EmergencyType.objects.all()
    districts = District.objects.all()
    citizen = Citizen.objects.get(loginid_id=request.session["lid"])
    if request.method == "POST":
        ty = request.POST.get('type')
        loc = request.POST.get('location')
        lat = request.POST.get('latitude')
        lon = request.POST.get('longitude')
        di = request.POST.get('district_id') # Get detected district
        desc = request.POST.get('description')
        img = request.FILES.get('image')

        etype = EmergencyType.objects.get(id=ty)
        district = District.objects.get(id=di)
        EmergencyReport.objects.create(user=citizen, emergency_type=etype, district=district, location_details=loc, latitude=lat, longitude=lon, description=desc, image=img)
        
        # Notify staff of THIS district
        staff_members = Staff.objects.filter(district=district)
        for s in staff_members:
            Notification.objects.create(user=s.loginid, message=f"NEW EMERGENCY: {etype.name} reported at {loc}")
            
        messages.success(request, "Emergency Reported. District authorities are notified.")
        return redirect("/citizen_view_reports")
    return render(request, 'CITIZEN/report_emergency.html', {'types': types, 'districts': districts})

def citizen_view_reports(request):
    citizen = Citizen.objects.get(loginid_id=request.session["lid"])
    reports = EmergencyReport.objects.filter(user=citizen).order_by('-reported_at')
    return render(request, 'CITIZEN/view_reports.html', {'reports': reports})

def citizen_request_rescue(request):
    id = request.GET.get("id")
    report = EmergencyReport.objects.get(id=id)
    citizen = Citizen.objects.get(loginid_id=request.session["lid"])
    if request.method == "POST":
        cp = request.POST.get('contact_person')
        ph = request.POST.get('phone')
        num = request.POST.get('number')
        pri = request.POST.get('priority')
        msg = request.POST.get('message')

        RescueRequest.objects.create(report=report, user=citizen, district=citizen.district, contact_person=cp, contact_phone=ph, number_of_people=num, priority=pri, message=msg)
        
        # Notify staff of this district
        staff_members = Staff.objects.filter(district=citizen.district)
        for s in staff_members:
            Notification.objects.create(user=s.loginid, message=f"RESCUE REQUESTED: For {report.emergency_type.name} at {report.location_details}")
            
        messages.success(request, "Rescue Request Sent")
        return redirect("/citizen_home")
    return render(request, 'CITIZEN/request_rescue.html', {'report': report})

def citizen_view_news(request):
    citizen = Citizen.objects.get(loginid_id=request.session["lid"])
    news = DistrictNews.objects.filter(district=citizen.district).order_by('-created_at')
    return render(request, 'CITIZEN/view_news.html', {'news': news})

def citizen_view_alerts(request):
    citizen = Citizen.objects.get(loginid_id=request.session["lid"])
    alerts = EmergencyAlert.objects.filter(district=citizen.district).order_by('-created_at')
    return render(request, 'CITIZEN/view_alerts.html', {'alerts': alerts})

def citizen_add_feedback(request):
    citizen = Citizen.objects.get(loginid_id=request.session["lid"])
    if request.method == "POST":
        sub = request.POST.get('subject')
        msg = request.POST.get('message')
        Feedback.objects.create(user=citizen, subject=sub, message=msg)
        messages.success(request, "Feedback Submitted")
        return redirect("/citizen_home")
    return render(request, 'CITIZEN/add_feedback.html')

def citizen_view_feedback(request):
    citizen = Citizen.objects.get(loginid_id=request.session["lid"])
    feedbacks = Feedback.objects.filter(user=citizen).order_by('-created_at')
    return render(request, 'CITIZEN/view_feedback.html', {'feedbacks': feedbacks})

def citizen_profile(request):
    citizen = Citizen.objects.get(loginid_id=request.session["lid"])
    return render(request, 'CITIZEN/profile.html', {'citizen': citizen})

def citizen_edit_profile(request):
    citizen = Citizen.objects.get(loginid_id=request.session["lid"])
    districts = District.objects.all()
    if request.method == "POST":
        n = request.POST.get('name')
        e = request.POST.get('email')
        ph = request.POST.get('phone')
        ad = request.POST.get('address')
        di = request.POST.get('district')
        pic = request.FILES.get('profile_pic')

        citizen.name = n
        citizen.email = e
        citizen.phone = ph
        citizen.address = ad
        citizen.district = District.objects.get(id=di)
        if pic:
            citizen.profile_pic = pic
        citizen.save()
        messages.success(request, "Profile Updated")
        return redirect("/citizen_profile")
    return render(request, 'CITIZEN/edit_profile.html', {'citizen': citizen, 'districts': districts})

def volunteer_profile(request):
    volunteer = Volunteer.objects.get(loginid_id=request.session["lid"])
    return render(request, 'VOLUNTEER/profile.html', {'volunteer': volunteer})

def volunteer_edit_profile(request):
    volunteer = Volunteer.objects.get(loginid_id=request.session["lid"])
    districts = District.objects.all()
    if request.method == "POST":
        n = request.POST.get('name')
        e = request.POST.get('email')
        ph = request.POST.get('phone')
        sk = request.POST.get('skills')
        di = request.POST.get('district')
        pic = request.FILES.get('profile_pic')

        volunteer.name = n
        volunteer.email = e
        volunteer.phone = ph
        volunteer.skills = sk
        volunteer.district = District.objects.get(id=di)
        if pic:
            volunteer.profile_pic = pic
        volunteer.save()
        messages.success(request, "Profile Updated")
        return redirect("/volunteer_profile")
    return render(request, 'VOLUNTEER/edit_profile.html', {'volunteer': volunteer, 'districts': districts})

def staff_profile(request):
    staff = Staff.objects.get(loginid_id=request.session["lid"])
    return render(request, 'STAFF/profile.html', {'staff': staff})

def staff_view_volunteers(request):
    staff = Staff.objects.get(loginid_id=request.session["lid"])
    volunteers = Volunteer.objects.filter(district=staff.district, status='Approved')
    return render(request, 'STAFF/view_volunteers.html', {'volunteers': volunteers})

def staff_view_citizens(request):
    staff = Staff.objects.get(loginid_id=request.session["lid"])
    citizens = Citizen.objects.filter(district=staff.district)
    return render(request, 'STAFF/view_citizens.html', {'citizens': citizens})

def staff_post_urgent_work(request):
    staff = Staff.objects.get(loginid_id=request.session["lid"])
    if request.method == "POST":
        ti = request.POST.get('title')
        ds = request.POST.get('description')
        UrgentWorkRequest.objects.create(staff=staff, district=staff.district, title=ti, description=ds)
        
        # Notify all volunteers in the district
        volunteers = Volunteer.objects.filter(district=staff.district, status='Approved')
        for v in volunteers:
            Notification.objects.create(user=v.loginid, message=f"URGENT WORK: {ti}")
            
        messages.success(request, "Urgent Work Request Broadcasted to District Volunteers")
        return redirect("/staff_home")
    return render(request, 'STAFF/post_urgent_work.html')

def staff_view_work_responses(request):
    staff = Staff.objects.get(loginid_id=request.session["lid"])
    responses = UrgentWorkResponse.objects.filter(request__staff=staff).order_by('-created_at')
    return render(request, 'STAFF/view_work_responses.html', {'responses': responses})

def volunteer_view_urgent_work(request):
    volunteer = Volunteer.objects.get(loginid_id=request.session["lid"])
    requests = UrgentWorkRequest.objects.filter(district=volunteer.district).order_by('-created_at')
    return render(request, 'VOLUNTEER/view_urgent_work.html', {'requests': requests})

def volunteer_accept_work(request, id):
    volunteer = Volunteer.objects.get(loginid_id=request.session["lid"])
    work_req = UrgentWorkRequest.objects.get(id=id)
    
    if request.method == "POST":
        msg = request.POST.get('message')
        # Check if already responded
        resp, created = UrgentWorkResponse.objects.get_or_create(request=work_req, volunteer=volunteer)
        resp.message = msg
        resp.status = "Accepted"
        resp.save()
        
        # Notify the staff member
        Notification.objects.create(user=work_req.staff.loginid, message=f"Volunteer {volunteer.name} accepted work: {work_req.title}")
        
        messages.success(request, "Work Request Accepted. Chat channel created.")
        return redirect(f"/chat_room/{work_req.staff.loginid.id}/")
    return render(request, 'VOLUNTEER/accept_work.html', {'work': work_req})

def chat_room(request, receiver_id):
    my_lid = request.session.get("lid")
    receiver = Login.objects.get(id=receiver_id)
    
    # Check if a response exists to authorize chat (security)
    # If staff is sender, receiver is volunteer. If volunteer is sender, receiver is staff.
    is_staff = Staff.objects.filter(loginid_id=my_lid).exists()
    is_volunteer = Volunteer.objects.filter(loginid_id=my_lid).exists()
    
    # Simple security: Only allow if they have an active work response together
    if is_staff:
        staff = Staff.objects.get(loginid_id=my_lid)
        volunteer = Volunteer.objects.get(loginid_id=receiver_id)
        if not UrgentWorkResponse.objects.filter(request__staff=staff, volunteer=volunteer, status='Accepted').exists():
             messages.error(request, "Unauthorized chat session.")
             return redirect("/")
    elif is_volunteer:
        volunteer = Volunteer.objects.get(loginid_id=my_lid)
        staff = Staff.objects.get(loginid_id=receiver_id)
        if not UrgentWorkResponse.objects.filter(request__staff=staff, volunteer=volunteer, status='Accepted').exists():
             messages.error(request, "Unauthorized chat session.")
             return redirect("/")
    else:
        return redirect("/")

    if request.method == "POST":
        msg = request.POST.get('message')
        if msg:
            ChatMessage.objects.create(sender_id=my_lid, receiver=receiver, message=msg)
        return redirect(f"/chat_room/{receiver_id}/")

    messages_list = ChatMessage.objects.filter(
        (models.Q(sender_id=my_lid) & models.Q(receiver=receiver)) |
        (models.Q(sender=receiver) & models.Q(receiver_id=my_lid))
    ).order_by('timestamp')
    
    # Mark messages as read
    ChatMessage.objects.filter(sender=receiver, receiver_id=my_lid, is_read=False).update(is_read=True)

    context = {
        'receiver': receiver,
        'messages_list': messages_list,
        'my_lid': my_lid
    }
    return render(request, 'chat_room.html', context)

def view_my_chats(request):
    my_lid = request.session.get("lid")
    if not my_lid:
        return redirect("/")
    
    # Find all people I have exchanged messages with
    sent_to = ChatMessage.objects.filter(sender_id=my_lid).values_list('receiver_id', flat=True)
    received_from = ChatMessage.objects.filter(receiver_id=my_lid).values_list('sender_id', flat=True)
    
    distinct_ids = set(list(sent_to) + list(received_from))
    chat_partners = []
    
    for pid in distinct_ids:
        partner = Login.objects.get(id=pid)
        # Try to find their name from Staff or Volunteer
        name = partner.username
        if Staff.objects.filter(loginid=partner).exists():
            name = Staff.objects.get(loginid=partner).name
        elif Volunteer.objects.filter(loginid=partner).exists():
            name = Volunteer.objects.get(loginid=partner).name
            
        last_msg = ChatMessage.objects.filter(
            (models.Q(sender_id=my_lid) & models.Q(receiver_id=pid)) |
            (models.Q(sender_id=pid) & models.Q(receiver_id=my_lid))
        ).last()
        
        chat_partners.append({
            'lid': pid,
            'name': name,
            'last_message': last_msg.message if last_msg else "",
            'time': last_msg.timestamp if last_msg else None,
            'unread': ChatMessage.objects.filter(sender_id=pid, receiver_id=my_lid, is_read=False).count()
        })
    
    chat_partners.sort(key=lambda x: x['time'] if x['time'] else x['time'], reverse=True)
        
    return render(request, 'view_my_chats.html', {'chats': chat_partners})

def staff_view_news(request):
    staff = Staff.objects.get(loginid_id=request.session["lid"])
    news = DistrictNews.objects.filter(district=staff.district).order_by('-created_at')
    return render(request, 'STAFF/view_news.html', {'news': news})

def staff_delete_news(request):
    id = request.GET.get("id")
    DistrictNews.objects.get(id=id).delete()
    messages.success(request, "News Deleted")
    return redirect("/staff_view_news")

def volunteer_view_news(request):
    volunteer = Volunteer.objects.get(loginid_id=request.session["lid"])
    news = DistrictNews.objects.filter(district=volunteer.district).order_by('-created_at')
    return render(request, 'VOLUNTEER/view_news.html', {'news': news})

# --- Notification AJAX Views ---

from django.http import JsonResponse

def get_notifications(request):
    if "lid" in request.session:
        notifications = Notification.objects.filter(user_id=request.session["lid"], is_read=False).order_by('-created_at')
        data = []
        for n in notifications:
            data.append({
                'id': n.id,
                'message': n.message,
                'time': n.created_at.strftime("%H:%M")
            })
            # Mark as read after fetching? Or let the user click? 
            # User mentioned "notification pop up", usually it shows once.
            n.is_read = True
            n.save()
        return JsonResponse({'notifications': data})
    return JsonResponse({'notifications': []})
