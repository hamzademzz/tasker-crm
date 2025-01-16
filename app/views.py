from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from .models import Customer, Tasker, File, RegularCustomer, CompletedJob
from .forms import CustomerForm

def home(request):
    customers = Customer.objects.all()
    taskers = Tasker.objects.all()  # Include taskers
    status_choices = Customer.STATUS_CHOICES  # Include status choices
    return render(request, 'app/home.html', {
        'customers': customers,
        'taskers': taskers,
        'status_choices': status_choices,
    })

def customer_create_view(request):
    if request.method == 'POST':
        # Collect data from POST request
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        service = request.POST.get('service')
        status = request.POST.get('status')
        notes = request.POST.get('notes') 
        date = request.POST.get('date') 
        price = request.POST.get('price') 
        assigned_tasker_id = request.POST.get('assigned_tasker')

        # Create a new Customer instance
        assigned_tasker = Tasker.objects.get(id=assigned_tasker_id) if assigned_tasker_id else None
        customer = Customer.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            service=service,
            status=status,
            notes=notes,  # Save notes
            assigned_tasker=assigned_tasker,
            date=date,
            price=price,
        )

        # Handle file attachments
        if request.FILES.getlist('attachments'):
            for file in request.FILES.getlist('attachments'):
                file_instance = File.objects.create(name=file.name, file=file)
                customer.attachments.add(file_instance)

        return redirect('home')


def customer_detail_view(request, customer_id):
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            raise Http404("Customer not found.")

        customer.name = request.POST.get('name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone')
        customer.address = request.POST.get('address')
        customer.service = request.POST.get('service')
        customer.status = request.POST.get('status')
        customer.notes = request.POST.get('notes')
        customer.date = request.POST.get('date')
        customer.price = request.POST.get('price')
     

        assigned_tasker_id = request.POST.get('assigned_tasker')
        if assigned_tasker_id:
            customer.assigned_tasker = Tasker.objects.get(id=assigned_tasker_id)
        else:
            customer.assigned_tasker = None

        customer.save()

        # Handle file attachments
        if request.FILES.getlist('attachments'):
            for file in request.FILES.getlist('attachments'):
                file_instance = File.objects.create(name=file.name, file=file)
                customer.attachments.add(file_instance)

        return redirect('home')


def regular_customer_detail(request):
    customers = Customer.objects.all()  # All customers for selection in the modal
    regular_customers = RegularCustomer.objects.all()  # Display all regular customers
    return render(request, 'app/regular_customer_detail.html', {
        'regular_customers': regular_customers,
        'customers': customers,
    })

def regular_customer_create_view(request):
    if request.method == 'POST':
        # Collect data from POST request
        customer_id = request.POST.get('customer')
        service_type = request.POST.get('service_type')
        last_service_date = request.POST.get('last_service_date')
        service_dates = request.POST.get('service_dates')  # Assuming this is a date string
        contract_details = request.POST.get('contract_details')

        # Get the customer instance
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'status': 'fail', 'message': 'Customer not found.'}, status=400)

        # Create a new RegularCustomer instance
        regular_customer = RegularCustomer.objects.create(
            customer=customer,
            service_type=service_type,
            last_service_date=last_service_date,
            service_dates=service_dates,
            contract_details=contract_details,
        )

        # Handle file uploads for invoice and other documents
        if 'invoice' in request.FILES:
            regular_customer.invoice = request.FILES['invoice']
        if 'other_documents' in request.FILES:
            regular_customer.other_documents = request.FILES['other_documents']

        regular_customer.save()


    return redirect('regular_customer_detail')


def edit_regular_customer(request, id):
    # Fetch the RegularCustomer object or return a 404 if not found
    regular_customer = get_object_or_404(RegularCustomer, id=id)

    if request.method == 'POST':
        # Get updated data from the POST request
        service_type = request.POST.get('service_type')
        last_service_date = request.POST.get('last_service_date')
        contract_details = request.POST.get('contract_details')

        # Check if the data exists before trying to save
        if not service_type or not last_service_date or not contract_details:
            return HttpResponse("Error: Missing required fields", status=400)

        # Update the regular customer fields
        regular_customer.service_type = service_type
        regular_customer.last_service_date = last_service_date
        regular_customer.contract_details = contract_details

        # Optional: Handle file uploads (invoice and other documents)
        if 'invoice' in request.FILES:
            regular_customer.invoice = request.FILES['invoice']
        if 'other_documents' in request.FILES:
            regular_customer.other_documents = request.FILES['other_documents']

        # Save the updated regular customer to the database
        regular_customer.save()

        # Return a success message or redirect
        return redirect('regular_customer_detail')

    # In case of GET request or incorrect method, redirect
    return redirect('regular_customer_detail')

    from .models import CompletedJob

def completed_jobs(request):
    completed_jobs = CompletedJob.objects.all()
    return render(request, 'app/completed_jobs.html', {'completed_jobs': completed_jobs})

def lead_jobs(request):
    lead_jobs = LeadJob.objects.all()
    return render(request, 'app/lead_jobs.html', {'lead_jobs': lead_jobs})