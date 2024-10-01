from django import forms
from .models import Registration
from user.models import User
from role.models import Role
from django.contrib.auth.hashers import make_password
class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    full_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}))

    class Meta:
        model = Registration
        fields = ['username', 'email', 'password1', 'password2', 'full_name']  # Added full_name
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        registration = super().save(commit=False)
        registration.password = make_password(self.cleaned_data["password1"])  
        registration.full_name = self.cleaned_data["full_name"]  

        if commit:
            registration.save()
            user_role = Role.objects.get(pk=4)  
            User.objects.create(
                username=registration.username,
                email=registration.email,
                password=registration.password, 
                full_name=registration.full_name, 
                role=user_role,  
                profile_picture_url='' 
            )

        return registration
    
from django import forms
from django.contrib.auth.hashers import check_password
from .models import Registration

class CustomLoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        try:
            user = Registration.objects.get(username=username)
            if not check_password(password, user.password):
                raise forms.ValidationError("Invalid username or password")

        except Registration.DoesNotExist:
            raise forms.ValidationError("Invalid username or password")

        cleaned_data['user'] = user
        return cleaned_data
