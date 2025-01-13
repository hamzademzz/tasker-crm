from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('customers/create/', views.customer_create_view, name='customer_create_view'),
    path('customer/<int:customer_id>/', views.customer_detail_view, name='customer_detail'),
]
