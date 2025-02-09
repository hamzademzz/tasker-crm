from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('customers/create/', views.customer_create_view, name='customer_create_view'),
    path('customer/<int:customer_id>/', views.customer_detail_view, name='customer_detail'),
    path('regular-customers/', views.regular_customer_detail, name='regular_customer_detail'),
    path('regular-customers/create/', views.regular_customer_create_view, name='regular_customer_create_view'),
    path('regular-customers/edit/<int:id>/', views.edit_regular_customer, name='edit_regular_customer'),
    path('completed-jobs/', views.completed_jobs, name='completed_jobs'),
    path('lead-jobs/', views.lead_jobs, name='lead_jobs'),
    path('export/', views.export_to_excel, name='export_to_excel'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('regular-customers/export/', views.export_regular_customers, name='export_regular_customers'),
    path('regular-customers/upload/', views.upload_regular_customer_excel, name='upload_regular_customer_excel'),
    path('export-completed-jobs/', views.export_completed_jobs, name='export_completed_jobs'),
    path('upload-completed-jobs/', views.upload_completed_jobs, name='upload_completed_jobs'),
    path('partners/', views.partners, name='partners'),  # Partner list page
    path('partners/save/', views.save_partner, name='save_partner'),  # Save Partner (Create or Update)
    path('partners/upload/', views.upload_partners, name='upload_partners'),  # Upload Partners Excel file
]
