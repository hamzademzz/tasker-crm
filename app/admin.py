from django.contrib import admin
from .models import Customer, RegularCustomer, Partner, Firm, Tasker

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
    list_display = ('name', 'category')

@admin.register(Firm)
class FirmAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner')

@admin.register(Tasker)
class TaskerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')
