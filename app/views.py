from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer
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


from django.shortcuts import render, redirect
from .models import Customer, Tasker, File

def customer_create_view(request):
    if request.method == 'POST':
        # Collect data from POST request
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        service = request.POST.get('service')
        status = request.POST.get('status')
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
            assigned_tasker=assigned_tasker,
        )

        # Handle file attachments
        if request.FILES.getlist('attachments'):
            for file in request.FILES.getlist('attachments'):
                file_instance = File.objects.create(name=file.name, file=file)
                customer.attachments.add(file_instance)

        customer.save()  # Save the customer object
        return redirect('home')  # Redirect to the home page

    # For GET request
    taskers = Tasker.objects.all()
    status_choices = Customer.STATUS_CHOICES
    return render(request, 'app/home.html', {
        'taskers': taskers,
        'status_choices': status_choices,
    })