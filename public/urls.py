"""
URL configuration for public project.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Public URLs
    path('', views.index),
    path('register/', views.register_public),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    
    # Admin URLs
    path('admin_home/', views.admin_home),
    path('admin_dashboard/', views.admin_home),
    path('admin_add_authority/', views.admin_add_authority),
    path('admin_view_authorities/', views.admin_view_authorities),
    path('admin_edit_authority/', views.admin_edit_authority),
    path('admin_block_authority/', views.admin_block_authority),
    path('admin_unblock_authority/', views.admin_unblock_authority),
    path('admin_view_requests/', views.admin_view_requests),
    path('admin_forward_request/', views.admin_forward_request),
    path('admin_view_feedback/', views.admin_view_feedback),
    path('admin_reply_feedback/', views.admin_reply_feedback),
    path('admin_view_customers/', views.admin_view_customers),
    path('admin_block_customer/', views.admin_block_customer),
    path('admin_unblock_customer/', views.admin_unblock_customer),
    path('admin_manage_schemes/', views.admin_manage_schemes),
    path('admin_add_scheme/', views.admin_add_scheme),
    path('admin_edit_scheme/', views.admin_edit_scheme),
    path('admin_view_news/', views.admin_view_news),
    path('admin_add_news/', views.admin_add_news),
    path('admin_edit_news/', views.admin_edit_news),
    path('admin_toggle_news_status/', views.admin_toggle_news_status),
    path('admin_total_reports/', views.admin_total_reports),
    path('admin_add_notice/', views.admin_add_notice),
    
    # Authority URLs
    path('authority_home/', views.authority_home),
    path('authority_view_requests/', views.authority_view_requests),
    path('authority_request_detail/', views.authority_request_detail),
    path('authority_issue_certificate/', views.authority_issue_certificate),
    path('authority_issued_certificates/', views.authority_issued_certificates),
    path('staff_view_scheme_applications/', views.staff_view_scheme_applications),
    path('staff_verify_scheme_application/', views.staff_verify_scheme_application),
    path('staff_view_complaints/', views.staff_view_complaints),
    path('staff_reply_complaint/', views.staff_reply_complaint),
    path('staff_view_notices/', views.staff_view_notices),
    
    # Customer URLs
    path('customer_home/', views.customer_home),
    path('customer_apply_certificate/', views.customer_apply_certificate),
    path('customer_applications/', views.customer_view_applications),
    path('customer_application_detail/', views.customer_application_detail),
    path('customer_payment/', views.customer_payment),
    path('customer_add_feedback/', views.customer_add_feedback),
    path('customer_view_feedback/', views.customer_view_feedback),
    path('customer_view_schemes/', views.customer_view_schemes),
    path('customer_apply_scheme/', views.customer_apply_scheme),
    path('customer_scheme_status/', views.customer_scheme_status),
    path('customer_scheme_application_detail/', views.customer_scheme_application_detail),
    path('customer_add_complaint/', views.customer_add_complaint),
    path('customer_view_complaints/', views.customer_view_complaints),
    path('customer_view_news/', views.customer_view_news),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
