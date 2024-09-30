from django import forms
from .models import User, UserProfile, Role, UserPersonalization

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

class UserProfileForm(forms.ModelForm):
    LEARNING_STYLE_CHOICES = [
        ('Visual', 'Visual'),
        ('Auditory', 'Auditory'),
        ('Logical', 'Logical'),
    ]
    
    INTEREST_CHOICES = [
        ('Technology', 'Technology'),
        ('Art', 'Art'),
        ('History', 'History'),
        ('Science', 'Science'),
        ('Business', 'Business'),
        ('Literature', 'Literature'),
        ('Music', 'Music'),
        ('Sports', 'Sports'),
        ('Cooking', 'Cooking'),
        ('Photography', 'Photography'),
        ('Psychology', 'Psychology'),
        ('Travel', 'Travel'),
        ('Fitness', 'Fitness'),
        ('Fashion', 'Fashion'),
        ('Philosophy', 'Philosophy'),
        ('Gardening','Gardening'),
        ('Architecture', 'Architecture'),
        ('Coding', 'Coding'),
        ('Economics', 'Economics'),
        ('Education', 'Education'),
        ('Biology', 'Biology'),
        ('Chemistry', 'Chemistry'),
        ('Mathematics', 'Mathematics'),
        ('Physics', 'Physics'),
        ('Film', 'Film'),
        
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
