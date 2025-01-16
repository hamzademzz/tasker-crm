from django.db import models
from django.utils.timezone import now


class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='customer_files/')

    def __str__(self):
        return self.name

from django.db import models
from django.utils.timezone import now

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
    assigned_tasker = models.ForeignKey('Tasker', on_delete=models.SET_NULL, null=True, blank=True)
    attachments = models.ManyToManyField(File, blank=True)
    notes = models.TextField(blank=True, null=True)
    date = models.DateField(default=now, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Check if the status is being set to 'Payment Done'
        if self.status == self.PAYMENT_DONE:
            # Create a new CompletedJob entry
            CompletedJob.objects.create(
                customer=self,
                service=self.service,
                completed_date=now(),
                price=self.price
            )
        
        # Check if the status is being set to 'Lead'
        if self.status == self.LEAD:
            # Create a new LeadJob entry
            LeadJob.objects.create(
                customer=self,
                name=self.name,
                email=self.email,
                phone=self.phone,
                address=self.address,
                service=self.service,
                status=self.status,
                assigned_tasker=self.assigned_tasker,
                attachments=self.attachments.all(),
                notes=self.notes,
                date=self.date,
                price=self.price,
                lead_date=now()
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CompletedJob(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service = models.CharField(max_length=255)
    completed_date = models.DateField(default=now)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.customer.name} - {self.service}"






from django.db import models

class RegularCustomer(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=255)
    last_service_date = models.DateField()
    service_dates = models.DateField(null=True, blank=True)  # This field will store the dates in JSON format, e.g., for recurring service dates.
    contract_details = models.TextField()
    invoice = models.FileField(upload_to='invoices/', null=True, blank=True)  # For storing invoices
    other_documents = models.FileField(upload_to='other_documents/', null=True, blank=True)  # For storing other documents

    def __str__(self):
        return self.customer.name


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
    tasks = models.ManyToManyField(Customer, related_name='assigned_tasks', blank=True)

    def __str__(self):
        return self.name
