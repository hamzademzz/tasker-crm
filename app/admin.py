from django.contrib import admin
from .models import Customer, RegularCustomer, Partner, Firm, Tasker, LeadJob, CompletedJob, File, Company

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'service', 'status')
    search_fields = ('name', 'email')

@admin.register(RegularCustomer)
class RegularCustomerAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service_type', 'last_service_date')
    search_fields = ('customer__name',)

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('industry',)

@admin.register(Company)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry')

@admin.register(Firm)
class FirmAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner')

@admin.register(Tasker)
class TaskerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')

@admin.register(LeadJob)
class LeadJobAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'lead_date', 'status', 'assigned_tasker')
    search_fields = ('customer__name', 'service', 'status')
    list_filter = ('lead_date', 'status')

@admin.register(CompletedJob)
class CompletedJobAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'completed_date', 'price')
    search_fields = ('customer__name', 'service')
    list_filter = ('completed_date',)

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'file')
    search_fields = ('name',)

# @admin.register(OpenJob)
# class CustomerAdmin(admin.ModelAdmin):
#     list_display = ('name', 'service', 'status', 'assigned_tasker', 'date', 'price')
#     search_fields = ('name', 'service')
#     list_filter = ('status', 'assigned_tasker', 'service', 'date')
