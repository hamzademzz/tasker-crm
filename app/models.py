from django.db import models
from django.utils.timezone import now


class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='customer_files/')

    def __str__(self):
        return self.name

class Customer(models.Model):
    PENDING = 'Pending'
    SITE_VISIT = 'Site Visit'
    QUOTE_SENT = 'Quote Sent'
    PAYMENT_DONE = 'Payment Done'
    LEAD = 'Lead'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SITE_VISIT, 'Site Visit'),
        (QUOTE_SENT, 'Quote Sent'),
        (PAYMENT_DONE, 'Payment Done'),
        (LEAD, 'Lead')
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    service = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    assigned_tasker = models.ForeignKey('Tasker', on_delete=models.SET_NULL, null=True, blank=True)  # Keep tasker reference here
    attachments = models.ManyToManyField(File, blank=True)
    notes = models.TextField(blank=True, null=True)
    date = models.DateField(default=now, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    industry = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Check if the status is being set to 'Payment Done'
        if self.status == self.PAYMENT_DONE:
            # Create a new CompletedJob entry
            CompletedJob.objects.create(
                customer=self,
                service=self.service,
                completed_date=now(),
                price=self.price,
                assigned_tasker=self.assigned_tasker  # Assign tasker here
            )
        
        # Check if the status is being set to 'Lead'
        if self.status == self.LEAD:
            # Create a new LeadJob entry with valid fields
            LeadJob.objects.create(
                customer=self,
                service=self.service,
                status=self.status,
                assigned_tasker=self.assigned_tasker,
                price=self.price,
                lead_date=now()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class LeadJob(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=15, null=True)
    address = models.TextField(null=True)  # Make nullable
    service = models.CharField(max_length=255)
    lead_date = models.DateField()
    status = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    assigned_tasker = models.ForeignKey('Tasker', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Lead for {self.customer.name} - {self.service}"


class CompletedJob(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.CharField(max_length=255)
    completed_date = models.DateField(default=now)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    assigned_tasker = models.ForeignKey('Tasker', on_delete=models.SET_NULL, null=True, blank=True)  # Link directly to Tasker

    def __str__(self):
        return f"{self.customer.name} - {self.service}"


class RegularCustomer(models.Model):
    CONTRACT_DETAILS_CHOICES = [
        ('Once a week', 'Once a week'),
        ('Twice a week', 'Twice a week'),
        ('Once a month', 'Once a month'),
        ('Twice a month', 'Twice a month'),
        ('3 times a month', '3 times a month'),
        ('Once every two months', 'Once every two months'),
        ('Twice every 2 months', 'Twice every 2 months'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=255)
    last_service_date = models.DateField()
    service_dates = models.DateField(null=True, blank=True)
    contract_details = models.CharField(
        max_length=50, 
        choices=CONTRACT_DETAILS_CHOICES, 
        default='Once a month'
    )
    invoice = models.FileField(upload_to='invoices/', null=True, blank=True)
    other_documents = models.FileField(upload_to='other_documents/', null=True, blank=True)

    def __str__(self):
        return f"{self.customer.name} - {self.service_type}"



class Partner(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Firm(models.Model):
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tasker(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return self.name
