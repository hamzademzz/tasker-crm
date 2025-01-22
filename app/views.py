from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from .models import Customer, Tasker, File, RegularCustomer, CompletedJob, LeadJob
from .forms import CustomerForm
from django.http import HttpResponse
import pandas as pd
from django.core.files.storage import default_storage
import os


def home(request):
    customers = Customer.objects.all()
    taskers = Tasker.objects.all()  # Include taskers
    status_choices = Customer.STATUS_CHOICES  # Include status choices
    regular_customers = RegularCustomer.objects.select_related('customer').all()  # Include regular customers
    return render(request, 'app/home.html', {
        'customers': customers,
        'taskers': taskers,
        'status_choices': status_choices,
        'regular_customers': regular_customers,  # Pass regular customers
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
        customer.industry = request.POST.get('industry')  # New field
        customer.company_name = request.POST.get('company_name')  # New field
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

        # Update customer fields with new values
        customer.name = request.POST.get('name')
        customer.email = request.POST.get('email')
        customer.phone = request.POST.get('phone')
        customer.address = request.POST.get('address')
        customer.service = request.POST.get('service')
        customer.status = request.POST.get('status')
        customer.notes = request.POST.get('notes')
        customer.date = request.POST.get('date')
        customer.price = request.POST.get('price')
        customer.industry = request.POST.get('industry')  # New field
        customer.company_name = request.POST.get('company_name')  # New field

        # Assign tasker if provided
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
        service_dates = request.POST.get('service_dates')
        contract_details = request.POST.get('contract_details')

        # Check if the data exists before trying to save
        if not service_type or not last_service_date or not contract_details:
            return HttpResponse("Error: Missing required fields", status=400)

        # Update the regular customer fields
        regular_customer.service_type = service_type
        regular_customer.last_service_date = last_service_date
        regular_customer.contract_details = contract_details
        regular_customer.service_dates = service_dates

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

def export_to_excel(request):
    customers = Customer.objects.all()
    data = [
        {
            "Name": customer.name,
            "Email": customer.email,
            "Phone": customer.phone,
            "Address": customer.address,
            "Service": customer.service,
            "Status": customer.status,
            "Date": customer.date,
            "Price": customer.price,
            "Industry": customer.industry,
            "Company Name": customer.company_name,
        }
        for customer in customers
    ]

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=customers.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Customers')

    return response

def upload_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        uploaded_file = request.FILES['excel_file']  # Uploaded file

        # Get the location where files are stored (this depends on your storage backend)
        storage_location = default_storage.location

        # Ensure the 'tmp' directory exists in the storage location
        tmp_dir = os.path.join(storage_location, 'tmp')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        try:
            # Save the file temporarily to the 'tmp' directory
            temp_file_path = os.path.join(tmp_dir, uploaded_file.name)
            with default_storage.open(temp_file_path, 'wb+') as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)

            # Now that the file is saved, load it using pandas
            df = pd.read_excel(temp_file_path)

            # Process each row of the Excel file
            for _, row in df.iterrows():
                name = row.get('Name')
                email = row.get('Email')
                phone = row.get('Phone')
                address = row.get('Address')
                service = row.get('Service')
                status = row.get('Status')
                price = row.get('Price')
                industry = row.get('Industry')
                company_name = row.get('Company Name')

                # Ensure the required fields are not empty
                if not name or not email:
                    continue  # Skip this row if required data is missing

                # Create or update the customer, allowing Django to handle the date
                Customer.objects.update_or_create(
                    email=email,
                    defaults={
                        'name': name,
                        'phone': phone,
                        'address': address,
                        'service': service,
                        'status': status,
                        'price': price,
                        'industry': industry,
                        'company_name': company_name,
                    },
                )

            # Optionally, delete the temporary file after processing
            default_storage.delete(temp_file_path)

            return redirect('home')
        except Exception as e:
            return HttpResponse(f"Error processing file: {str(e)}", status=500)

    return redirect('home')


def export_regular_customers(request):
    regular_customers = RegularCustomer.objects.all()
    data = [
        {
            "Name": rc.customer.name,
            "Service Type": rc.service_type,
            "Last Service Date": rc.last_service_date,
            "Service Dates": rc.service_dates,
            "Contract Details": rc.contract_details,
        }
        for rc in regular_customers
    ]

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=regular_customers.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Regular Customers')

    return response


def upload_regular_customer_excel(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        uploaded_file = request.FILES['excel_file']

        try:
            df = pd.read_excel(uploaded_file)

            for _, row in df.iterrows():
                customer_name = row.get('Name')
                service_type = row.get('Service Type')
                last_service_date = row.get('Last Service Date')
                service_dates = row.get('Service Dates')
                contract_details = row.get('Contract Details')

                if not customer_name or not service_type or not last_service_date:
                    continue

                customer = Customer.objects.filter(name=customer_name).first()
                if not customer:
                    continue

                RegularCustomer.objects.update_or_create(
                    customer=customer,
                    defaults={
                        'service_type': service_type,
                        'last_service_date': last_service_date,
                        'service_dates': service_dates,
                        'contract_details': contract_details,
                    },
                )

            return redirect('regular_customer_detail')
        except Exception as e:
            return HttpResponse(f"Error processing file: {str(e)}", status=500)

    return redirect('regular_customer_detail')
