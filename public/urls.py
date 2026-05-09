from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public URLs
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register_citizen/', views.register_citizen, name='register_citizen'),
    path('register_volunteer/', views.register_volunteer, name='register_volunteer'),
    
    # Admin URLs
    path('admin_home/', views.admin_home, name='admin_home'),
    path('admin_manage_districts/', views.admin_manage_districts, name='admin_manage_districts'),
    path('admin_add_district/', views.admin_add_district, name='admin_add_district'),
    path('admin_manage_staff/', views.admin_manage_staff, name='admin_manage_staff'),
    path('admin_add_staff/', views.admin_add_staff, name='admin_add_staff'),
    path('admin_approve_volunteers/', views.admin_approve_volunteers, name='admin_approve_volunteers'),
    path('admin_manage_emergency_types/', views.admin_manage_emergency_types, name='admin_manage_emergency_types'),
    path('admin_add_emergency_type/', views.admin_add_emergency_type, name='admin_add_emergency_type'),
    path('admin_view_all_reports/', views.admin_view_all_reports, name='admin_view_all_reports'),
    path('admin_send_alert/', views.admin_send_alert, name='admin_send_alert'),
    path('admin_view_feedback/', views.admin_view_feedback, name='admin_view_feedback'),
    
    # Staff URLs
    path('staff_home/', views.staff_home, name='staff_home'),
    path('staff_view_reports/', views.staff_view_reports, name='staff_view_reports'),
    path('staff_verify_report/<int:report_id>/', views.staff_verify_report, name='staff_verify_report'),
    path('staff_view_rescue_requests/', views.staff_view_rescue_requests, name='staff_view_rescue_requests'),
    path('staff_assign_volunteers/<int:request_id>/', views.staff_assign_volunteers, name='staff_assign_volunteers'),
    path('staff_update_situation/<int:report_id>/', views.staff_update_situation, name='staff_update_situation'),
    path('staff_broadcast_alert/', views.staff_broadcast_alert, name='staff_broadcast_alert'),
    
    # Volunteer URLs
    path('volunteer_home/', views.volunteer_home, name='volunteer_home'),
    path('volunteer_view_assignments/', views.volunteer_view_assignments, name='volunteer_view_assignments'),
    path('volunteer_update_status/', views.volunteer_update_status, name='volunteer_update_status'),
    path('volunteer_view_emergency_map/', views.volunteer_view_emergency_map, name='volunteer_view_emergency_map'),
    
    # Citizen URLs
    path('citizen_home/', views.citizen_home, name='citizen_home'),
    path('citizen_report_emergency/', views.citizen_report_emergency, name='citizen_report_emergency'),
    path('citizen_view_reports/', views.citizen_view_reports, name='citizen_view_reports'),
    path('citizen_request_rescue/<int:report_id>/', views.citizen_request_rescue, name='citizen_request_rescue'),
    path('citizen_view_alerts/', views.citizen_view_alerts, name='citizen_view_alerts'),
    path('citizen_add_feedback/', views.citizen_add_feedback, name='citizen_add_feedback'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
