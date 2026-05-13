from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Public URLs
    path('', views.index),
    path('login/', views.login_view),
    path('logout/', views.signout),
    path('register_citizen/', views.register_citizen),
    path('register_volunteer/', views.register_volunteer),

    # Admin URLs
    path('admin_home/', views.admin_home),
    path('admin_manage_districts/', views.admin_manage_districts),
    path('admin_add_district/', views.admin_add_district),
    path('admin_edit_district/', views.admin_edit_district),
    path('admin_delete_district/', views.admin_delete_district),
    path('admin_manage_staff/', views.admin_manage_staff),
    path('admin_add_staff/', views.admin_add_staff),
    path('admin_edit_staff/', views.admin_edit_staff),
    path('admin_staff_status/', views.admin_staff_status),
    path('admin_approve_volunteers/', views.admin_approve_volunteers),
    path('admin_volunteer_action/', views.admin_volunteer_action),
    path('admin_manage_emergency_types/', views.admin_manage_emergency_types),
    path('admin_add_emergency_type/', views.admin_add_emergency_type),
    path('admin_delete_emergency_type/', views.admin_delete_emergency_type),
    path('admin_view_all_reports/', views.admin_view_all_reports),
    path('admin_send_alert/', views.admin_send_alert),
    path('admin_view_feedback/', views.admin_view_feedback),
    path('admin_reply_feedback/', views.admin_reply_feedback),
    path('admin_view_citizens/', views.admin_view_citizens),

    # Citizen URLs
    path('citizen_home/', views.citizen_home),
    path('citizen_report_emergency/', views.citizen_report_emergency),
    path('citizen_view_reports/', views.citizen_view_reports),
    path('citizen_request_rescue/', views.citizen_request_rescue),
    path('citizen_view_alerts/', views.citizen_view_alerts),
    path('citizen_add_feedback/', views.citizen_add_feedback),
    path('citizen_view_feedback/', views.citizen_view_feedback),
    path('citizen_profile/', views.citizen_profile),
    path('citizen_edit_profile/', views.citizen_edit_profile),

    # Volunteer URLs
    path('volunteer_home/', views.volunteer_home),
    path('volunteer_view_assignments/', views.volunteer_view_assignments),
    path('volunteer_update_status/', views.volunteer_update_status),
    path('volunteer_update_rescue/', views.volunteer_update_rescue),
    path('volunteer_view_emergency_map/', views.volunteer_view_emergency_map),
    path('volunteer_profile/', views.volunteer_profile),
    path('volunteer_edit_profile/', views.volunteer_edit_profile),

    # Staff URLs
    path('staff_home/', views.staff_home),
    path('staff_view_reports/', views.staff_view_reports),
    path('staff_verify_report/', views.staff_verify_report),
    path('staff_view_rescue_requests/', views.staff_view_rescue_requests),
    path('staff_assign_volunteers/', views.staff_assign_volunteers),
    path('staff_update_situation/', views.staff_update_situation),
    path('staff_broadcast_alert/', views.staff_broadcast_alert),
    path('staff_profile/', views.staff_profile),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
