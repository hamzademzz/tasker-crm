from django.urls import path
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from . import views
from .views import CustomLoginView, home, tasker
from django.contrib.auth.views import LogoutView 

# Restriction for non-admin users
def admin_only(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.username != 'admin':
            return redirect('tasker')  # Redirect non-admins to tasker
        return view_func(request, *args, **kwargs)
    return wrapper

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),  # Custom login page
    path('', login_required(admin_only(home)), name='home'),
    path('tasker/', tasker, name='tasker'),  # Tasker page accessible to all users
    path('customers/create/', login_required(admin_only(views.customer_create_view)), name='customer_create_view'),
    path('customer/<int:customer_id>/', login_required(admin_only(views.customer_detail_view)), name='customer_detail'),
    path('regular-customers/', login_required(admin_only(views.regular_customer_detail)), name='regular_customer_detail'),
    path('regular-customers/create/', login_required(admin_only(views.regular_customer_create_view)), name='regular_customer_create_view'),
    path('regular-customers/edit/<int:id>/', login_required(admin_only(views.edit_regular_customer)), name='edit_regular_customer'),
    path('completed-jobs/', login_required(views.completed_jobs), name='completed_jobs'),
    path('lead-jobs/', login_required(admin_only(views.lead_jobs)), name='lead_jobs'),
    path('export/', login_required(admin_only(views.export_to_excel)), name='export_to_excel'),
    path('upload-excel/', login_required(admin_only(views.upload_excel)), name='upload_excel'),
    path('regular-customers/export/', login_required(admin_only(views.export_regular_customers)), name='export_regular_customers'),
    path('regular-customers/upload/', login_required(admin_only(views.upload_regular_customer_excel)), name='upload_regular_customer_excel'),
    path('export-completed-jobs/', login_required(admin_only(views.export_completed_jobs)), name='export_completed_jobs'),
    path('upload-completed-jobs/', login_required(admin_only(views.upload_completed_jobs)), name='upload_completed_jobs'),
    path('partners/', login_required(admin_only(views.partners)), name='partners'),
    path('partners/save/', login_required(admin_only(views.save_partner)), name='save_partner'),
    path('partners/upload/', login_required(admin_only(views.upload_partners)), name='upload_partners'),
    path('skip_hire/', login_required(admin_only(views.skip_hire)), name='skip_hire'),
    path('accounts/logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('open_jobs/', views.open_jobs, name='open_jobs'),
    # path('open_jobs/view/<int:id>/', views.view_open_job, name='view_open_job'),  # View job page
]