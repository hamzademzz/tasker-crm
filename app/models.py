from django.db import models


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

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SITE_VISIT, 'Site Visit'),
        (QUOTE_SENT, 'Quote Sent'),
        (PAYMENT_DONE, 'Payment Done'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    service = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    assigned_tasker = models.ForeignKey('Tasker', on_delete=models.SET_NULL, null=True, blank=True)
    attachments = models.ManyToManyField(File, blank=True)
    notes = models.TextField(blank=True, null=True)  # Add notes field

    def __str__(self):
        return self.name





class RegularCustomer(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    service_type = models.CharField(max_length=255)
    last_service_date = models.DateField()
    contract_details = models.TextField()

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
