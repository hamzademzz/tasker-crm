from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('customers/create/', views.customer_create_view, name='customer_create_view'),
    path('customer/<int:customer_id>/', views.customer_detail_view, name='customer_detail'),
    path('regular-customers/', views.regular_customer_detail, name='regular_customer_detail'),
    path('regular-customers/create/', views.regular_customer_create_view, name='regular_customer_create_view'),  # Updated path
    path('regular-customers/edit/<int:id>/', views.edit_regular_customer, name='edit_regular_customer'),
    path('completed-jobs/', views.completed_jobs, name='completed_jobs'),
    path('lead-jobs/', views.lead_jobs, name='lead_jobs'),
]
