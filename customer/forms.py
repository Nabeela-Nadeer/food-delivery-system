from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import CustomerProfile

class CustomerSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to widgets
        for field_name, field in self.fields.items():
            css_class = 'form-control'
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' ' + css_class
            else:
                field.widget.attrs['class'] = css_class

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            CustomerProfile.objects.create(
                user=user,
                address=self.cleaned_data.get('address', ''),
                phone=self.cleaned_data.get('phone', '')
            )
        return user

from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['address', 'phone']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
