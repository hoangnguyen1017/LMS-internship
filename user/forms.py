from django import forms
from .models import User, UserProfile, Role, UserPersonalization

from django.contrib.auth.hashers import make_password
import re
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'full_name', 'role', 'profile_picture_url']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter full name'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'profile_picture_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter profile picture URL'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')

        # Check password length
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        
        # Check for number
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one number.")
        
        # Check for special character
        if not re.search(r'[@$!%*?&]', password):
            raise forms.ValidationError("Password must contain at least one special character (@, $, !, %, *, ?, &).")
        
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        # Mã hóa mật khẩu trước khi lưu
        if self.cleaned_data['password']:
            user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
class UserProfileForm(forms.ModelForm):
    LEARNING_STYLE_CHOICES = [
        ('Visual', 'Visual'),
        ('Auditory', 'Auditory'),
        ('Reading/Writing', 'Reading/Writing'),
        ('Kinesthetic', 'Kinesthetic'),
    ]
    
    INTEREST_CHOICES = [
        ('Technology', 'Technology'),
        ('Art', 'Art'),
        ('Business', 'Business'),
    ]

    learning_style = forms.ChoiceField(choices=LEARNING_STYLE_CHOICES, required=True)
    interests = forms.ChoiceField(choices=INTEREST_CHOICES, required=True)  # Thay đổi từ MultipleChoiceField thành ChoiceField

    class Meta:
        model = UserProfile
        fields = ['bio', 'interests', 'learning_style', 'preferred_language']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 1, 'cols': 40, 'class': 'form-control'}),
            'preferred_language': forms.TextInput(attrs={'class': 'form-control'}),
        }
class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role_name']
        widgets = {
            'role_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter role name'}),
        }

class UserPersonalizationForm(forms.ModelForm):
    class Meta:
        model = UserPersonalization
        fields = ['recommended_courses', 'personalized_learning_path', 'learning_style']
        widgets = {
            'recommended_courses': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Enter recommended courses...'}),
            'personalized_learning_path': forms.Textarea(attrs={'rows': 5, 'class': 'form-control', 'placeholder': 'Describe the learning path...'}),
        }

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(label="Upload Excel File")