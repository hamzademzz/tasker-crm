from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, Http404
from .models import Customer, Tasker, File, RegularCustomer, CompletedJob, LeadJob
from .forms import CustomerForm
from django.http import HttpResponse
import pandas as pd
from django.core.files.storage import default_storage
import os

from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

# Custom LoginView to handle redirection based on the username
class CustomLoginView(LoginView):
    template_name = 'app/login.html'

    def get_success_url(self):
        # Check the username and redirect accordingly
        if self.request.user.username == 'admin':
            return reverse_lazy('home')  # Redirect to home (admin should see home)
        else:
            return reverse_lazy('tasker')  # Redirect to tasker for other users

@login_required
def tasker(request):
    return render(request, 'app/tasker.html')

@login_required
def home(request):
    customers = Customer.objects.all()
    taskers = Tasker.objects.all()  # Include taskers
    status_choices = Customer.STATUS_CHOICES  # Include status choices
    regular_customers = RegularCustomer.objects.select_related('customer').all()  # Include regular customers

    partners = Partner.objects.all()  # Retrieve all partners
    companies = Company.objects.all()  # Retrieve all companies
    return render(request, 'app/home.html', {
        'customers': customers,
        'taskers': taskers,
        'status_choices': status_choices,
        'regular_customers': regular_customers,  # Pass regular customers
        'partners': partners,
        'companies': companies,
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

        # Retrieve the Partner instance if an industry is provided
        industry = None
        industry_name = request.POST.get('industry')
        if industry_name:
            try:
                industry = Partner.objects.get(industry=industry_name)
            except Partner.DoesNotExist:
                pass  # Skip if the industry does not exist

        # Retrieve the Company instance if a company name is provided
        company = None
        company_name = request.POST.get('company_name')
        if company_name:
            try:
                company = Company.objects.get(name=company_name)
            except Company.DoesNotExist:
                pass  # Skip if the company does not exist

        # Retrieve assigned tasker if provided
        assigned_tasker = Tasker.objects.filter(id=assigned_tasker_id).first() if assigned_tasker_id else None

        # Create a new Customer instance
        customer = Customer.objects.create(
            name=name,
            email=email,
            phone=phone,
            address=address,
            service=service,
            status=status,
            notes=notes,
            assigned_tasker=assigned_tasker,
            date=date,
            price=price
        )

        # Assign the Partner instance and Company instance to the customer if they exist
        if industry:
            customer.industry = industry
        if company:
            customer.company_name = company

        # Save the customer after assigning the foreign key relationships
        customer.save()

        # Handle file attachments
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

        # Retrieve the Partner instance based on the selected industry
        industry_name = request.POST.get('industry')
        if industry_name:
            try:
                industry = Partner.objects.get(industry=industry_name)
                customer.industry = industry
            except Partner.DoesNotExist:
                # You may want to handle this error (e.g., notify the user)
                pass

        # Retrieve the Company instance based on the selected company name
        company_name = request.POST.get('company_name')
        if company_name:
            try:
                company = Company.objects.get(name=company_name)
                customer.company_name = company
            except Company.DoesNotExist:
                # You may want to handle this error (e.g., notify the user)
                pass

        # Assign tasker if provided
        assigned_tasker_id = request.POST.get('assigned_tasker')
        if assigned_tasker_id:
            try:
                customer.assigned_tasker = Tasker.objects.get(id=assigned_tasker_id)
            except Tasker.DoesNotExist:
                # You may want to handle this error (e.g., notify the user)
                customer.assigned_tasker = None
        else:
            customer.assigned_tasker = None

        # Save the updated customer instance
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

from django.shortcuts import render
from .models import Customer, Tasker

def completed_jobs(request):
    # Initialize the completed_jobs list
    completed_jobs = []
    tasker_details = None  # Variable to store tasker details
    
    # Check if the logged-in user is "admin" or a tasker
    if request.user.username == 'admin':
        # If the user is admin, show all jobs (CompletedJob entries)
        completed_jobs = CompletedJob.objects.all()
    else:
        try:
            # Find the Tasker where email matches the username (case-insensitive)
            tasker = Tasker.objects.get(email__iexact=request.user.username)  # case-insensitive check
            
            # Store tasker details to pass to the template
            tasker_details = f"Tasker Name: {tasker.name}, Email: {tasker.email}"
            
            # Get jobs assigned to this Tasker using the assigned_tasker field in CompletedJob
            completed_jobs = CompletedJob.objects.filter(assigned_tasker=tasker)
        except Tasker.DoesNotExist:
            # If no Tasker exists for this user, keep the completed_jobs as an empty list
            completed_jobs = []
    
    return render(request, 'app/completed_jobs.html', {
        'completed_jobs': completed_jobs,
        'tasker_details': tasker_details
    })

def open_jobs(request):
    # Initialize the open_jobs list
    open_jobs = []
    tasker_details = None  # Variable to store tasker details

    # Check if the logged-in user is "admin" or a tasker
    if request.user.username == 'admin':
        # If the user is admin, show all open jobs (Customer entries with statuses 'Pending', 'Site Visit', 'Quote Sent')
        open_jobs = Customer.objects.filter(status__in=[Customer.PENDING, Customer.SITE_VISIT, Customer.QUOTE_SENT])
    else:
        try:
            # Find the Tasker where email matches the username (case-insensitive)
            tasker = Tasker.objects.get(email__iexact=request.user.username)  # case-insensitive check

            # Store tasker details to pass to the template
            tasker_details = f"Tasker Name: {tasker.name}, Email: {tasker.email}"

            # Get jobs assigned to this Tasker that are open (Pending, Site Visit, or Quote Sent)
            open_jobs = Customer.objects.filter(assigned_tasker=tasker, status__in=[Customer.PENDING, Customer.SITE_VISIT, Customer.QUOTE_SENT])
        except Tasker.DoesNotExist:
            # If no Tasker exists for this user, keep the open_jobs as an empty list
            open_jobs = []

    return render(request, 'app/open_jobs.html', {
        'open_jobs': open_jobs,
        'tasker_details': tasker_details
    })


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
            "Industry": getattr(customer.industry, 'industry', 'N/A'),  # Avoids error
            "Company Name": getattr(customer.company_name, 'name', 'N/A'),  # Avoids error
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


def export_completed_jobs(request):
    completed_jobs = CompletedJob.objects.all()
    data = [
        {
            "Customer Name": cj.customer.name,
            "Service": cj.service,
            "Completed Date": cj.completed_date,  # Keep as Completed Date
            "Price": cj.price,
        }
        for cj in completed_jobs
    ]

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=completed_jobs.xlsx'
    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Completed Jobs')

    return response

def upload_completed_jobs(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        uploaded_file = request.FILES['excel_file']
        try:
            # Read the Excel file into a DataFrame
            df = pd.read_excel(uploaded_file)

            # Ensure the 'Completed Date' column is in the correct date format
            df['Completed Date'] = pd.to_datetime(df['Completed Date'], errors='coerce')

            # Check for invalid dates
            if df['Completed Date'].isnull().any():
                return HttpResponse("Error: Invalid date format in the file.", status=400)

            # Iterate over the DataFrame rows and save to the database
            for _, row in df.iterrows():
                # Get the customer instance by name
                customer_name = row['Customer Name']
                customer = Customer.objects.filter(name=customer_name).first()

                # If the customer does not exist, create a new one (optional)
                if not customer:
                    customer = Customer.objects.create(name=customer_name)

                # Create a new CompletedJob entry
                CompletedJob.objects.create(
                    customer=customer,                       # ForeignKey
                    service=row['Service'],                  # CharField
                    completed_date=row['Completed Date'].date(),  # DateField
                    price=row['Price']                       # DecimalField
                )
            return redirect('completed_jobs')  # Redirect to the completed jobs page
        except Exception as e:
            return HttpResponse(f"Error processing file: {str(e)}", status=500)
    return HttpResponse("Invalid request method.", status=400)

from django.shortcuts import render, redirect
from .models import Partner
from django.http import HttpResponse
import pandas as pd

# Display the list of partners and provide create/update functionality
def partners(request):
    partners_list = Partner.objects.all()
    return render(request, 'app/partners.html', {'partners': partners_list})

# Handle Partner Create/Update
def save_partner(request):
    if request.method == 'POST':
        partner_id = request.POST.get('partner_id')
        name = request.POST.get('name')
        category = request.POST.get('category')

        # If partner_id is provided, update existing partner, otherwise create new one
        if partner_id:
            partner = Partner.objects.get(id=partner_id)
            partner.name = name
            partner.category = category
            partner.save()
        else:
            # Create a new partner
            Partner.objects.create(name=name, category=category)

        return redirect('partners')  # Redirect back to partners page

# Handle Excel File Upload for Partners
def upload_partners(request):
    if request.method == 'POST' and request.FILES.get('excel_file'):
        uploaded_file = request.FILES['excel_file']
        try:
            df = pd.read_excel(uploaded_file)

            # Check for necessary columns
            required_columns = ['Partner Name', 'Category']
            if not all(col in df.columns for col in required_columns):
                return HttpResponse("Error: Missing required columns.", status=400)

            for _, row in df.iterrows():
                Partner.objects.update_or_create(
                    name=row['Partner Name'],
                    category=row['Category']
                )

            return redirect('partners')  # Redirect to the partner list page

        except Exception as e:
            return HttpResponse(f"Error processing file: {str(e)}", status=500)

    return HttpResponse("Invalid request method.", status=400)

def skip_hire(request):
    return render(request, 'app/skip_hire.html')


from django.http import JsonResponse
from .models import Company

from django.http import JsonResponse

def get_companies(request):
    industry_name = request.GET.get("industry")
    try:
        partner = Partner.objects.get(industry=industry_name)  # Get the partner by industry name
        companies = partner.companies.all()  # Get the related companies (customers)
        company_list = [{"company": company.name} for company in companies]  # Change name to company
        return JsonResponse({"companies": company_list})
    except Partner.DoesNotExist:
        return JsonResponse({"error": "Industry not found"})


def save_industry(request):
    if request.method == "POST":
        industry_name = request.POST.get("industry")
        if industry_name:
            Partner.objects.create(industry=industry_name)
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": "Invalid data"})
    return JsonResponse({"success": False, "error": "Invalid request"})

def industry_list(request):
    industries = Partner.objects.all()  # Fetches all Partner objects
    return render(request, "app/partners.html", {"industries": industries})


    
# def open_jobs(request):
#     # Filter customers with the specified statuses
#     open_jobs = Customer.objects.filter(status__in=[Customer.PENDING, Customer.SITE_VISIT, Customer.QUOTE_SENT])

#     return render(request, 'open_jobs.html', {'open_jobs': open_jobs})


def get_customers_by_industry(request):
    company_name = request.GET.get('company_name')
    print("Company Name received:", company_name)  # Debug: log the received company name

    if company_name:
        try:
            # Get the company by name (assuming company name is unique)
            company = get_object_or_404(Company, name=company_name)
            print("Company found:", company.name)  # Debug: log the found company name

            # Fetch customers for the given company name
            customers = Customer.objects.filter(company_name=company)
            print("Customers found:", customers.count())  # Debug: log the number of customers found

            if customers.exists():
                customer_data = [
                    {
                        'id': customer.id,
                        'name': customer.name,
                        'email': customer.email,
                        'phone': customer.phone,
                        'address':customer.address
                        # Add more customer fields as needed
                    }
                    for customer in customers
                ]
                return JsonResponse({'customers': customer_data})
            else:
                return JsonResponse({'message': 'No customers found for this company.'}, status=404)
        except Exception as e:
            print(f"Error: {e}")  # Debug: log any error during company lookup
            return JsonResponse({'error': f'Error: {e}'}, status=500)
    else:
        return JsonResponse({'error': 'No company_name provided'}, status=400)
