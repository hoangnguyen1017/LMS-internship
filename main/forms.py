# main/forms.py
from django import forms
from user.models import User  # Sử dụng model User của Django
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail  # Thêm hàm gửi email
from django.conf import settings  # Để lấy email mặc định từ settings
from role.models import Role
from user.models import Profile
import random
class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'}))
    first_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}))
    last_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}))

    class Meta:
        model = User  # Use Django's default User model
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']  # Include first name and last name
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password1"]
        user.password = make_password(password)  # Hash the password
        user.first_name = self.cleaned_data['first_name']  # Save first name
        user.last_name = self.cleaned_data['last_name']  # Save last name
        user.email = self.cleaned_data['email']  # Save email

        if commit:
            user.save()
            user_role = Role.objects.get(role_name='User')  
            profile = Profile.objects.create(user=user, role=user_role)
            random_number = random.randint(1000, 9999)

            # Send confirmation email after successful registration
            send_mail(
                'Account Registration Successful',
                f'Hello {user.username},\n\n'
                f'You have successfully registered an account on the system.\n\n'
                f'Your login information:\n'
                f'Username: {user.username}\n'
                f'Password: {password}\n'
                f'Your confirmation code is: {random_number}',
                settings.DEFAULT_FROM_EMAIL,  # Sender email
                [user.email],  # User's email
                fail_silently=False,
            )
        return user

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Email')

class PasswordResetCodeForm(forms.Form):
    code = forms.CharField(label='Authentication Code')
    
class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm new password")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Password and Confirm password is not match.")
from django import forms
from django.contrib.auth import authenticate

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid login credentials.")
        return cleaned_data


