from django import forms
from .models import Customer, File, Tasker

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address', 'service', 'status', 'assigned_tasker', 'attachments']
    
    # Attachments - Handle multiple file selections
    attachments = forms.ModelMultipleChoiceField(queryset=File.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)

    # Tasker - Allow selecting a Tasker from a dropdown list
    assigned_tasker = forms.ModelChoiceField(queryset=Tasker.objects.all(), required=False)  # Updated to ModelChoiceField
