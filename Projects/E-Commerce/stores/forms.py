from django import forms
from .models import Store

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ['name', 'description', 'address', 'phone_number', 'email', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        } 